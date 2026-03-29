import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import requests
from io import BytesIO

class KLineClassifier:
    def __init__(self, model_name='resnet18', num_classes=3, pretrained=True):
        """
        初始化K线分类器
        
        参数:
            model_name: 使用的模型名称 ('resnet18', 'resnet50', 'vgg16', 等)
            num_classes: 分类类别数量 (例如: 3类 - 看涨, 看跌, 中性)
            pretrained: 是否使用预训练权重
        """
        self.model_name = model_name
        self.num_classes = num_classes
        self.pretrained = pretrained
        
        # 初始化模型
        self.model = self._initialize_model()
        
        # 定义图像预处理转换
        self.transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                                 std=[0.229, 0.224, 0.225])
        ])
        
        # 定义类别标签 (根据你的实际任务调整)
        self.class_names = ['Bullish', 'Bearish', 'Neutral']
    
    def _initialize_model(self):
        """初始化预训练模型"""
        try:
            if self.model_name == 'resnet18':
                model = models.resnet18(pretrained=self.pretrained)
            elif self.model_name == 'resnet50':
                model = models.resnet50(pretrained=self.pretrained)
            elif self.model_name == 'vgg16':
                model = models.vgg16(pretrained=self.pretrained)
            elif self.model_name == 'efficientnet_b0':
                model = models.efficientnet_b0(pretrained=self.pretrained)
            else:
                raise ValueError(f"不支持的模型: {self.model_name}")
            
            # 修改最后一层全连接层以适应我们的分类任务
            if hasattr(model, 'classifier') and isinstance(model.classifier, nn.Sequential):
                # 对于VGG等模型
                in_features = model.classifier[-1].in_features
                model.classifier[-1] = nn.Linear(in_features, self.num_classes)
            elif hasattr(model, 'fc'):
                # 对于ResNet等模型
                in_features = model.fc.in_features
                model.fc = nn.Linear(in_features, self.num_classes)
            else:
                raise ValueError("无法确定模型分类器的结构")
                
            return model
            
        except Exception as e:
            print(f"初始化模型时出错: {e}")
            return None
    
    def load_weights(self, model_path):
        """加载训练好的权重"""
        try:
            self.model.load_state_dict(torch.load(model_path))
            print(f"成功加载模型权重: {model_path}")
            return True
        except Exception as e:
            print(f"加载模型权重时出错: {e}")
            return False
    
    def predict(self, image_path_or_url, visualize=True):
        """
        对K线图像进行预测
        
        参数:
            image_path_or_url: 本地图像路径或图像URL
            visualize: 是否可视化图像和预测结果
            
        返回:
            预测结果和置信度
        """
        if self.model is None:
            return "模型未初始化", 0
        
        # 加载图像
        try:
            if image_path_or_url.startswith('http'):
                response = requests.get(image_path_or_url)
                image = Image.open(BytesIO(response.content)).convert('RGB')
            else:
                image = Image.open(image_path_or_url).convert('RGB')
        except Exception as e:
            return f"加载图像时出错: {e}", 0
        
        # 预处理图像
        input_tensor = self.transform(image)
        input_batch = input_tensor.unsqueeze(0)  # 创建批处理维度
        
        # 设置模型为评估模式
        self.model.eval()
        
        # 进行预测
        with torch.no_grad():
            output = self.model(input_batch)
            
        # 应用softmax获取概率
        probabilities = torch.nn.functional.softmax(output[0], dim=0)
        confidence, predicted_idx = torch.max(probabilities, 0)
        predicted_class = self.class_names[predicted_idx.item()]
        
        # 可视化结果
        if visualize:
            self._visualize_prediction(image, predicted_class, confidence.item())
        
        return predicted_class, confidence.item()
    
    def _visualize_prediction(self, image, predicted_class, confidence):
        """可视化图像和预测结果"""
        plt.figure(figsize=(10, 5))
        
        # 显示图像
        plt.subplot(1, 2, 1)
        plt.imshow(np.array(image))
        plt.axis('off')
        plt.title('Input K-line Chart')
        
        # 显示预测结果
        plt.subplot(1, 2, 2)
        plt.text(0.1, 0.6, f'Prediction: {predicted_class}\nConfidence: {confidence:.2f}', 
                 fontsize=14, ha='left')
        plt.axis('off')
        plt.title('Prediction Result')
        
        plt.tight_layout()
        plt.show()

# 使用示例
if __name__ == "__main__":
    # 初始化分类器
    classifier = KLineClassifier(model_name='resnet18', num_classes=3)
    
    # 如果你有训练好的模型权重，可以加载它们
    # classifier.load_weights('path/to/your/model_weights.pth')
    
    # 使用示例图像进行预测 (这里使用一个占位URL，实际使用时请替换为你的K线图)
    # 你可以使用本地路径或URL
    image_path = fr"E:\stock\backtest\image\000063.SZ_analysis\000063.SZ_analysis_20220104_20220106.png"  # 替换为你的图像路径或URL
    
    # 进行预测
    try:
        prediction, confidence = classifier.predict(image_path)
        print(f"预测结果: {prediction}, 置信度: {confidence:.2f}")
    except Exception as e:
        print(f"预测过程中出错: {e}")