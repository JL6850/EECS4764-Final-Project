from app import app
from flask import jsonify, request, render_template, redirect, url_for

last_data = None

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/test', methods=['GET'])
def test():
    # 渲染页面
    return render_template('test.html')

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