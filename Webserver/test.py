import requests
import time
# 定义URL
url = "http://127.0.0.1:5000/api/test"
url = "http://34.123.213.115:5000/api/test"

# 定义多个 payload 列表
payloads = [
    {
        "action": "normal_summon",
        "location_9": 1,
        "card_id": 41777
    },
    {
        "action": "normal_summon",
        "location_10": 1,
        "card_id": 44818
    },
    {
        "action": "normal_summon",
        "location_11": 1,
        "card_id": 62121
    },
    {
        "action": "tribute_summon",
        "location_11": 0,
        "location_12": 1,
        "card_id": 10000
    },
    {
        "action": "set",
        "location_16": 1,
        "card_id": 50755
    },
    {
        "action": "change_position_to_attack_position",
        "location_12": 1,
        "card_id": 10000
    },
    {
        "action": "change_position_to_defence_position",
        "location_12": 1,
        "card_id": 10000
    },
    {
        "action": "change_position_to_attack_position",
        "location_12": 1,
        "card_id": 10000
    },
    {
        "action": "banish",
        "location_9": 0,
        "location_10": 0,
        "location_12": 0,
        "location_16": 0,
        "card_id": 10000
    },
]

# 循环发送每个 payload
for i, payload in enumerate(payloads, start=1):
    try:
        print(f"Testing payload {i}: {payload}")
        response = requests.post(url, json=payload)
        print(f"Response {i} status code:", response.status_code)
        print(f"Response {i} body:", response.json())
    except Exception as e:
        print(f"Error during payload {i}: {e}")
    finally:
        # 每次发送后等待 1 秒
        time.sleep(1)