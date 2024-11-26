from app import app
from flask import jsonify, request, render_template, redirect, url_for, send_from_directory
import os
last_data = None

@app.route('/')
@app.route('/index')
def index():
    return render_template('card-display.html')

# @app.route('/test', methods=['GET'])
# def test():
#     # 渲染页面
#     return render_template('test.html')

# 配置图片文件路径
@app.route('/data/card/<filename>')
def card_images(filename):
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../Data/Card'))
    file_path = os.path.join(base_path, filename)
    print(f"访问图片文件: {file_path}")
    if not os.path.exists(file_path):
        print("文件不存在！")
    return send_from_directory(base_path, filename)

@app.route('/api/data', methods=['GET'])
def get_data():
    # 返回最新数据
    global last_data
    if last_data is None:
        return jsonify({"error": "No data available."}), 200
    return jsonify({"data": last_data}), 200

@app.route('/api/test', methods=['POST'])
def test_json():
    global last_data
    # 接收 JSON 数据
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON data received"}), 400

    # 更新全局变量
    last_data = data
    return jsonify({"message": "JSON received successfully!", "data": data}), 200