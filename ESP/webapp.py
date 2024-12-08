
import requests
import time
import asyncio
import os
import shutil
import whisper
import json
from flask import Flask, request, jsonify
import threading
import gradio as gr
from llm_interpretation import get_llm_response_with_system_prompt  # 从 llm_interpretation 导入函数

# Whisper 模型加载
whisper_model = whisper.load_model("tiny.en").to("cpu")

# Flask 应用配置
app = Flask(__name__)
sensor_changes = {}

@app.route("/", methods=["POST"])
def receive_sensor_data():
    global sensor_changes
    try:
        sensor_changes = request.get_json()
        return jsonify({"status": "received", "data": sensor_changes}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

def start_flask_server():
    app.run(host="0.0.0.0", port=8080, debug=False, use_reloader=False)

flask_thread = threading.Thread(target=start_flask_server)
flask_thread.daemon = True
flask_thread.start()

def update_location_with_sensor_data(llm_json, sensor_values=None):
    global sensor_changes
    sensor_data = sensor_values or sensor_changes

    if not isinstance(llm_json, dict):
        raise ValueError("Expected llm_json to be a dictionary")

    # 将传感器数据按照原先的逻辑更新为 location_key 的形式
    if sensor_data:
        for key, value in sensor_data.items():
            llm_json[f"location_{key}"] = value

    return llm_json

# 您要发送 JSON 的目标服务器 URL
API_URL = "http://35.239.154.61:5000/api/test"

# 是否本地测试的开关（True：本地测试不发请求，只打印）
LOCAL_TEST = False

def process_input(audio=None, file=None, text_input=None, sensor_input=None):
    try:
        transcription = None

        # 处理文本输入
        if text_input:
            transcription = text_input
        elif audio or file:
            audio_input = audio if audio else file.name
            save_path = os.path.join(os.getcwd(), "input_audio.wav")
            shutil.copy(audio_input, save_path)
            if not save_path.endswith(".wav"):
                return "Error: Audio format is not WAV", "", "", ""
            transcription = whisper_model.transcribe(save_path)["text"]

        if transcription is None:
            return "No input provided", "", "", ""

        llm_response = get_llm_response_with_system_prompt(transcription)
        if isinstance(llm_response, dict) and "error" in llm_response:
            return transcription, "", "", llm_response["error"]

        sensor_values = None
        if sensor_input:
            try:
                sensor_values = json.loads(sensor_input.strip())
            except json.JSONDecodeError:
                return transcription, "", "", "Invalid sensor input format. Provide JSON like {'3':1}"

        # 将传感器数据合成到JSON中
        updated_json = update_location_with_sensor_data(llm_response, sensor_values)

        # 准备显示原始传感器数据（以收到的原始JSON形式）
        raw_sensor_data = sensor_values if sensor_values else sensor_changes
        raw_sensor_str = json.dumps(raw_sensor_data, indent=4) if raw_sensor_data else ""

        if LOCAL_TEST:
            # 本地测试：不发送请求，只打印和展示结果
            print("Transcription/Command:", transcription)
            print("Final JSON:\n", json.dumps(updated_json, indent=4))
            print("Raw Sensor Data:\n", raw_sensor_str)
            print("Status: Local test success.")
            return transcription, json.dumps(updated_json, indent=4), raw_sensor_str, "Local test success."
        else:
            # 正常发送请求到服务器
            try:
                response = requests.post(API_URL, json=updated_json)
                if response.status_code == 200:
                    return transcription, json.dumps(updated_json, indent=4), raw_sensor_str, "Successfully sent JSON to server."
                else:
                    return transcription, json.dumps(updated_json, indent=4), raw_sensor_str, f"Failed to send JSON. Status code: {response.status_code}, Response: {response.text}"
            except Exception as e:
                return transcription, json.dumps(updated_json, indent=4), raw_sensor_str, f"Error when sending JSON: {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}", "", "", ""

ui = gr.Interface(
    inputs=[
        gr.Audio(sources="microphone", type="filepath", label="Voice Input", format="wav"),
        gr.File(label="Upload Audio File"),
        gr.Textbox(label="Text Input (Command)", lines=2, placeholder="Type your command here..."),
        gr.Textbox(label="Sensor Input (JSON)", lines=2, placeholder='{"3":1, "5":0}')
    ],
    fn=process_input,
    outputs=[
        gr.Textbox(label="Transcription/Command"),
        gr.Textbox(label="Final JSON"),
        gr.Textbox(label="Received Sensor Data (Raw)"),
        gr.Textbox(label="Status")
    ],
    title="Voice & Text Assistant with Sensor Integration",
    description="Combine sensor data with voice or text input to generate actionable JSON and print raw sensor data on the webpage.",
    allow_flagging="never"
)

if __name__ == "__main__":
    ui.launch(debug=False, share=True)