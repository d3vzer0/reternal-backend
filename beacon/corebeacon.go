package main

import (
	"bytes"
	"crypto/sha1"
	"encoding/hex"
	"encoding/json"
	"fmt"
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

func main() {
	generate_id()
	start_beacon()
}

func generate_id() {
	machine_id, machine_error := machineid.ID()
	if machine_error != nil {
		os.Exit(3)
	}
	concat_id := machine_id + beacon_username
	base_sha := sha1.New()
	base_sha.Write([]byte(concat_id))
	beacon_id = hex.EncodeToString(base_sha.Sum(nil))
}

func beacon_data() []byte {
	base_content := map[string]interface{}{"beacon_id": beacon_id, "platform": beacon_platform, "timer": beacon_timer, "data": map[string]string{}}
	json_content, _ := json.Marshal(base_content)
	return json_content
}

func send_pulse() interface{} {
	core_json := beacon_data()
	response, response_error := http.Post(base_url, "application/json", bytes.NewBuffer(core_json))
	if response_error != nil {
		// fmt.Println(response_error)
		_ = response_error
	}
	response_content, read_error := ioutil.ReadAll(response.Body)
	if read_error != nil {
		// fmt.Println(read_error)
		_ = read_error
	}

	var json_values interface{}
	json_response := json.Unmarshal(response_content, &json_values)
	if json_response != nil {
		// fmt.Println(json_response)
		_ = json_response
	}
	return json_values
}

func start_pulse() {
	fmt.Println(send_pulse())
}

func start_beacon() {
	for exit_process == false {
		go start_pulse()
		time.Sleep(time.Duration(beacon_timer) * time.Second)
	}
}
