import ujson
import usocket
from machine import Pin, ADC
import time

# 配置GPIO引脚
s0 = Pin(14, Pin.OUT)  # S0 控制信号
s1 = Pin(12, Pin.OUT)  # S1 控制信号
s2 = Pin(13, Pin.OUT)  # S2 控制信号
s3 = Pin(15, Pin.OUT)  # S3 控制信号

mux_pins = [s0, s1, s2, s3]
adc = ADC(0)
sensor_count = 13

SERVER_IP = "192.168.1.100"  # 替换为服务器的IP地址
SERVER_PORT = 8080

# 函数：设置MUX选择信号
def set_mux_channel(channel):
    binary = [int(b) for b in '{:04b}'.format(channel)]
    for i in range(4):
        mux_pins[i].value(binary[i])

# 函数：读取光传感器的值
def get_light_sensor_values():
    sensor_data = {}
    for i in range(sensor_count):
        set_mux_channel(i)
        time.sleep(0.01)
        value = adc.read()
        sensor_data[f"Sensor_{i}"] = value
    return sensor_data

# 函数：检测传感器变化
def detect_sensor_changes(prev_data, current_data):
    changes = {}
    for sensor, value in current_data.items():
        if sensor in prev_data and prev_data[sensor] != value:
            changes[sensor] = value
    return changes

# 函数：发送数据到服务器
def send_data_to_server(data):
    try:
        addr = usocket.getaddrinfo(SERVER_IP, SERVER_PORT)[0][-1]
        sock = usocket.socket()
        sock.connect(addr)
        sock.send(ujson.dumps(data))
        sock.close()
        print("Data sent to server:", data)
    except Exception as e:
        print("Error sending data:", str(e))

# 主程序
def main():
    prev_sensor_data = get_light_sensor_values()
    while True:
        current_sensor_data = get_light_sensor_values()
        changes = detect_sensor_changes(prev_sensor_data, current_sensor_data)
        if changes:
            send_data_to_server(changes)
        prev_sensor_data = current_sensor_data
        time.sleep(0.5)

if __name__ == "__main__":
    main()