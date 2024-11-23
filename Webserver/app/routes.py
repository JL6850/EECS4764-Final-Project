from app import app
from flask import jsonify, request, render_template, redirect, url_for

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/test', methods=['GET', 'POST'])
def test():
    if request.method == 'POST':
        # 接收 POST 数据
        data = request.get_json()
        if not data:
            return render_template('test.html', error="No JSON data received.")

        # 将数据存储在全局变量中（或更好的方式是缓存/数据库）
        app.config['LAST_DATA'] = data

        # 重定向到 GET 请求，以刷新页面
        return redirect(url_for('test'))

    # GET 请求：渲染页面并显示数据
    data = app.config.get('LAST_DATA', None)
    return render_template('test.html', data=data)


@app.route('/api/test', methods=['POST'])
def test_json():
    # 接收 JSON 数据
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON data received"}), 400

    # 返回 JSON 响应
    return jsonify({
        "message": "JSON received successfully!",
        "received_data": data
    }), 200