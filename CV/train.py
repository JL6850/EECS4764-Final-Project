import os
import json
from tqdm import tqdm
import torch
import torchvision.transforms as transforms
from torch.utils.data import DataLoader, Dataset
from torchvision.models import resnet18
import torch.nn as nn
import torch.optim as optim
from PIL import Image

# 自定义数据集类
class CardDataset(Dataset):
    def __init__(self, root_dir, transform=None):
        self.root_dir = root_dir
        self.transform = transform

        # 找到所有图片文件
        self.images = [img for img in os.listdir(root_dir) if img.endswith(('.jpg', '.png', '.jpeg'))]

        # 提取卡牌编号（忽略序号部分）
        self.labels = [int(img.split('_')[0]) for img in self.images]

        # 创建编号到索引的映射
        original_labels = sorted(set(self.labels))  # 找到所有唯一卡牌编号
        self.label_map = {str(original_label): idx for idx, original_label in enumerate(original_labels)}

        # 将编号映射为索引
        self.labels = [self.label_map[str(label)] for label in self.labels]

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):
        img_path = os.path.join(self.root_dir, self.images[idx])
        image = Image.open(img_path).convert('RGB')
        label = self.labels[idx]
        if self.transform:
            image = self.transform(image)
        return image, label

# 数据预处理
transform = transforms.Compose([
    transforms.Resize((224, 224)),               # 调整到统一大小
    transforms.RandomHorizontalFlip(p=0.5),     # 随机水平翻转
    transforms.RandomRotation(15),              # 随机旋转 ±15 度
    transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),  # 调整亮度、对比度、饱和度
    transforms.RandomCrop(224, padding=4),      # 随机裁剪，带边缘填充
    transforms.ToTensor(),                      # 转为张量
    transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5]),  # 标准化
])

# 加载数据
train_dataset = CardDataset(root_dir='/Users/danielshi/PycharmProjects/recognition/data/train/', transform=transform)
train_loader = DataLoader(train_dataset, batch_size=8, shuffle=True)

# 保存标签映射到文件
label_map_path = "label_map.json"
with open(label_map_path, 'w') as f:
    json.dump(train_dataset.label_map, f)
print(f"标签映射已保存到 {label_map_path}")

# 定义模型
model = resnet18(pretrained=False)
model.fc = nn.Linear(model.fc.in_features, len(train_dataset.label_map))  # 使用类别数动态调整输出层

# 定义损失函数和优化器
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.0001)

# 检查设备
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")
model.to(device)  # 模型加载到设备上

# 训练过程
num_epochs = 50
for epoch in range(num_epochs):
    model.train()
    running_loss = 0.0
    correct_predictions = 0
    total_samples = 0

    progress_bar = tqdm(train_loader, desc=f"Epoch {epoch + 1}/{num_epochs}")
    for images, labels in progress_bar:
        images, labels = images.to(device), labels.to(device)  # 转移到设备

        # 前向传播
        outputs = model(images)
        loss = criterion(outputs, labels)

        # 反向传播和优化
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        # 记录损失
        running_loss += loss.item()

        # 计算正确预测数量
        _, predicted = torch.max(outputs, 1)
        correct_predictions += (predicted == labels).sum().item()
        total_samples += labels.size(0)

        # 更新进度条
        progress_bar.set_postfix(loss=running_loss / len(train_loader))

    # 计算准确率
    accuracy = correct_predictions / total_samples * 100
    print(f"Epoch [{epoch + 1}/{num_epochs}], Loss: {running_loss / len(train_loader):.4f}, Accuracy: {accuracy:.2f}%")

# 保存模型
torch.save(model.state_dict(), 'model.pth')
print("训练完成，模型已保存！")
