import network
import socket
import machine
import time
import ujson
from machine import Pin

s0 = Pin(15, Pin.OUT)
s1 = Pin(0, Pin.OUT)
s2 = Pin(14, Pin.OUT)
s3 = Pin(12, Pin.OUT)
mux_pins = [s0, s1, s2, s3]

mux_signal = Pin(13, Pin.IN)

sensor_count = 13
sensor_key_map = {
    0: 3,
    1: 5,
    2: 8,
    3: 9,
    4: 10,
    5: 11,
    6: 12,
    7: 13,
    8: 16,
    9: 17,
    10: 18,
    11: 19,
    12: 20
}

SERVER_IP = "10.206.112.89"
SERVER_PORT = 8080

def connect_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Connecting to network...")
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            pass
    print("Connected to", ssid)
    print("IP Address:", wlan.ifconfig()[0])

def set_mux_channel(channel):
    for i in range(4):
        bit_value = (channel >> i) & 1
        mux_pins[i].value(bit_value)
    time.sleep(0.001)

def get_light_sensor_values():
    sensor_data = {}
    for i in range(sensor_count):
        set_mux_channel(i)
        time.sleep(0.005)
        digital_value = mux_signal.value()
        sensor_data[i] = digital_value
    return sensor_data

def detect_stable_sensor_changes(prev_data, current_data, stability_time, stable_states):
    changes = {}
    current_time = time.time()

    for sensor_idx, value in current_data.items():
        if sensor_idx in prev_data and prev_data[sensor_idx] != value:
            stable_states[sensor_idx] = {"value": value, "timestamp": current_time}
        elif sensor_idx in stable_states:
            elapsed_time = current_time - stable_states[sensor_idx]["timestamp"]
            if stable_states[sensor_idx]["value"] == value and elapsed_time >= stability_time:
                mapped_key = str(sensor_key_map[sensor_idx])
                changes[mapped_key] = value

    stable_states = {
        sensor: state
        for sensor, state in stable_states.items()
        if time.time() - state["timestamp"] < stability_time
    }

    return changes, stable_states

def send_data_to_server(data):
    try:
        addr = socket.getaddrinfo(SERVER_IP, SERVER_PORT)[0][-1]
        sock = socket.socket()
        sock.connect(addr)

        json_data = ujson.dumps(data)

        request = (
            "POST / HTTP/1.1\r\n"
            "Host: {}\r\n"
            "Content-Type: application/json\r\n"
            "Content-Length: {}\r\n"
            "Connection: close\r\n\r\n"
            "{}"
        ).format(SERVER_IP, len(json_data), json_data)

        sock.send(request.encode('utf-8'))
        response = sock.recv(1024)
        print("Server response:", response)
        sock.close()
        print("Data sent to server:", data)
    except Exception as e:
        print("Error sending data:", str(e))

def main():
    connect_wifi("Columbia University", "")
    prev_sensor_data = get_light_sensor_values()
    stable_states = {}
    stability_time = 1.5

    while True:
        current_sensor_data = get_light_sensor_values()
        changes, stable_states = detect_stable_sensor_changes(
            prev_sensor_data, current_sensor_data, stability_time, stable_states
        )

        print("Real-time sensor values:", current_sensor_data)

        if changes:
            print("Stable changes:", changes)
            send_data_to_server(changes)

        prev_sensor_data = current_sensor_data
        time.sleep(0.5)

main()