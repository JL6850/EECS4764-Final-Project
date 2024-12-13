import os
import time
import cv2
import torch
from torchvision import transforms
from torchvision.models import resnet18
from PIL import Image
import json
import requests
import numpy as np

# 切换到项目根目录
os.chdir('/Users/danielshi/PycharmProjects/recognition')

# 加载训练好的模型
def load_trained_model(model_path, num_classes):
    model = resnet18(pretrained=False)
    model.fc = torch.nn.Linear(model.fc.in_features, num_classes)
    model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
    model.eval()
    return model

# 加载标签映射
def load_label_map(label_map_path):
    with open(label_map_path, 'r') as f:
        label_map = json.load(f)

    label_map = {int(k): v for k, v in label_map.items()}
    reverse_label_map = {v: k for k, v in label_map.items()}

    return label_map, reverse_label_map

# 加载ID和Name映射
# 加载ID和Name映射
def load_id_name_mapping(file_path):
    id_name_mapping = {}
    with open(file_path, 'r') as f:
        for line in f:
            parts = line.strip().split(maxsplit=1)  # 使用空格作为分隔符
            if len(parts) == 2:
                try:
                    id_name_mapping[int(parts[0])] = parts[1]
                except ValueError:
                    print(f"跳过无效行: {line.strip()}")
    return id_name_mapping


# 图像预处理
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5]),
])

# 图像推理函数
def predict_image(model, image, transform, reverse_label_map):
    image = transform(image).unsqueeze(0)
    with torch.no_grad():
        outputs = model(image)
        probabilities = torch.softmax(outputs, dim=1)
        _, predicted = torch.max(probabilities, 1)

    predicted_id = predicted.item()
    predicted_label = reverse_label_map.get(predicted_id, "Unknown Category")
    return predicted_label

# 实时摄像头推理函数
def real_time_camera(model, transform, reverse_label_map, id_name_mapping, stream_url="http://192.168.1.227:81/stream", server_url="http://127.0.0.1:5000/api/test", interval=1.0):
    cap = cv2.VideoCapture(stream_url)  # 使用本地摄像头
    if not cap.isOpened():
        print("无法打开摄像头")
        return

    last_detection_time = time.time()  # 初始化检测时间
    edges = np.zeros((1280, 720), dtype=np.uint8)  # 根据摄像头分辨率设置大小

    while True:
        ret, frame = cap.read()
        if not ret:
            print("无法读取摄像头帧")
            break

        current_time = time.time()

        # 每隔 interval 秒检测一次
        if current_time - last_detection_time >= interval:
            last_detection_time = current_time

            # 转换为灰度图
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # 边缘检测
            edges = cv2.Canny(gray, 30, 100)

            # 膨胀操作合并相邻区域
            kernel = np.ones((3, 3), np.uint8)
            edges = cv2.dilate(edges, kernel, iterations=1)

            # 找轮廓
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            cropped_cards = []

            # 合并重叠矩形框
            detected_boxes = []
            for contour in contours:
                # 面积过滤
                area = cv2.contourArea(contour)
                if area < 10000 :
                    continue

                # 使用 cv2.boundingRect 检测
                x, y, w, h = cv2.boundingRect(contour)

                # 长宽比过滤
                aspect_ratio = float(w) / h
                if aspect_ratio < 0.7 or aspect_ratio > 1.5:
                    continue

                # 检查是否与已检测的框重叠
                overlap = False
                for xb, yb, wb, hb in detected_boxes:
                    if (x < xb + wb and x + w > xb and y < yb + hb and y + h > yb):
                        overlap = True
                        break
                if not overlap:
                    detected_boxes.append((x, y, w, h))
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                    # 提取卡牌区域
                    padding = 10
                    x_p, y_p = max(0, x - padding), max(0, y - padding)
                    w_p, h_p = min(frame.shape[1], w + 2 * padding), min(frame.shape[0], h + 2 * padding)
                    card_image = frame[y_p:y_p + h_p, x_p:x_p + w_p]
                    if card_image.size == 0:
                        continue
                    if card_image.size != 0:
                        cropped_cards.append(card_image)  # 保存裁剪的卡牌图像

                        # 显示裁剪出来的卡牌图像
                    for i, card in enumerate(cropped_cards):
                        cv2.imshow(f"Cropped Card {i + 1}", card)

                    # 转换为 PIL 图像并推理
                    card_image_pil = Image.fromarray(cv2.cvtColor(card_image, cv2.COLOR_BGR2RGB))
                    predicted_label = predict_image(model, card_image_pil, transform, reverse_label_map)

                    card_name = id_name_mapping.get(int(predicted_label), "Unknown Name")

                    if predicted_label != "Unknown Category":
                        # 创建发送的 JSON 数据
                        payload = {
                            "action": "video_check",
                            "card_id": int(predicted_label),
                            "card_name": card_name
                        }
                        try:
                            response = requests.post(server_url, json=payload)
                            if response.status_code == 200:
                                print(f"Card ID: {predicted_label}, Name: {card_name}, Response: {response.json()}")
                            else:
                                print(f"发送失败，状态码: {response.status_code}")
                        except Exception as e:
                            print(f"发送数据到服务器失败: {e}")

                    # 在原始帧上显示卡牌 ID 和名称
                    cv2.putText(frame, f"ID: {predicted_label}, Name: {card_name}", (x, y - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # 显示原始帧和边缘检测效果
        cv2.imshow("Card Detection and Identification", frame)
        edges_display = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)  # 转换为彩色显示一致
        cv2.imshow("Edge Detection", edges_display)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    model_path = 'model.pth'
    label_map_path = 'label_map.json'
    id_name_mapping_path = 'duizhao_formatted.txt'

    # 加载标签映射
    label_map, reverse_label_map = load_label_map(label_map_path)

    # 加载ID和名称映射
    id_name_mapping = load_id_name_mapping(id_name_mapping_path)

    # 加载模型
    num_classes = len(label_map)
    model = load_trained_model(model_path, num_classes)
    # HTTP 流媒体地址
    stream_url = "http://192.168.1.227:81/stream"
    # 实时推理并发送到服务器
    real_time_camera(model, transform, reverse_label_map, id_name_mapping, stream_url=stream_url, server_url="http://35.232.41.243:5000/api/test")
