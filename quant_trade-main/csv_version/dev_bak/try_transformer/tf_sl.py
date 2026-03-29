import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import seaborn as sns
import warnings
import torch.nn.functional as F
warnings.filterwarnings('ignore')

# 配置设置
class Config:
    SEED = 42
    BATCH_SIZE = 64
    EPOCHS = 800
    LEARNING_RATE = 0.001
    HIDDEN_DIM = 128
    DROPOUT_RATE = 0.3
    WEIGHT_DECAY = 1e-5
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    MODEL_PATH = 'supervised_trading_model.pth'

# 设置随机种子
def set_seed(seed):
    torch.manual_seed(seed)
    np.random.seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

set_seed(Config.SEED)


# 修改损失函数 - 简化版本
class SimpleExpertLoss(nn.Module):
    def __init__(self, class_weights=None):
        super().__init__()
        if class_weights is not None:
            self.ce_loss = nn.CrossEntropyLoss(weight=class_weights)
        else:
            self.ce_loss = nn.CrossEntropyLoss()
        
    def forward(self, outputs, targets):
        # 只使用标准交叉熵损失
        return self.ce_loss(outputs, targets)


# 增强模型架构
class EnhancedTradingModel(nn.Module):
    def __init__(self, input_dim, hidden_dim=256, output_dim=3, dropout_rate=0.3):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            
            nn.Linear(hidden_dim, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            
            nn.Linear(hidden_dim, hidden_dim//2),
            nn.BatchNorm1d(hidden_dim//2),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            
            nn.Linear(hidden_dim//2, hidden_dim//4),
            nn.BatchNorm1d(hidden_dim//4),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            
            nn.Linear(hidden_dim//4, output_dim)
        )
        # 初始化权重
        self._init_weights()
        
    def _init_weights(self):
        for m in self.net.modules():
            if isinstance(m, nn.Linear):
                nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.BatchNorm1d):
                nn.init.constant_(m.weight, 1)
                nn.init.constant_(m.bias, 0)
                
    def forward(self, x):
        return self.net(x)


# 数据准备和预处理
def prepare_data(file_path, window_size=30, test_size=0.2, weight_method='manual'):
    # 加载数据
    df = pd.read_csv(file_path, index_col='trade_date', parse_dates=True)
    
    # 移除不必要的列
    df = df.drop(columns=['circ_mv', 'support', 'resistance', 'ts_code'], errors='ignore')
    df['action'] = df['action'].astype(int)
    df = df.dropna()
    # 选择特征列 (排除目标列和日期列)
    feature_cols = [col for col in df.columns if col not in ['action', 'trade_date',  'ts_code']]
    
    # 创建序列数据
    X, y = create_sequences(df, feature_cols, window_size)
    
    # 分割训练集和测试集
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=Config.SEED, shuffle=False
    )
    # 在数据预处理中添加检查
    print(f"数据中NaN值数量: {np.isnan(X_train).sum()}")
    print(f"数据中无穷大值数量: {np.isinf(X_train).sum()}")
    # 标准化特征
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)
    
    print(f"训练集大小: {X_train.shape[0]}, 测试集大小: {X_test.shape[0]}")
    print(f"输入维度: {X_train.shape[1]}")
    
    # 计算类别权重以处理不平衡数据
    # 修改计算类别权重的代码，确保y是整数类型
    class_counts = np.bincount(y.astype(int))  # 确保y是整数类型
    # 计算类别权重
    class_counts = np.bincount(y.astype(int))
    print(f"类别样本数量: {class_counts}")
    
    if weight_method == 'inverse':
        # 逆频率权重
        class_weights = 1.0 / class_counts
    elif weight_method == 'log':
        # 对数缩放权重
        class_weights = 1.0 / np.log(1.02 + class_counts)
    elif weight_method == 'sqrt':
        # 平方根缩放权重
        class_weights = 1.0 / np.sqrt(class_counts)
    elif weight_method == 'effective':
        # 有效样本数权重
        beta = 0.999
        effective_n = (1 - np.power(beta, class_counts)) / (1 - beta)
        class_weights = 1.0 / effective_n
    elif weight_method == 'manual':
        # 手动设置权重
        class_weights = np.array([0.02, 0.49, 0.49])  # 根据需求调整
    else:
        # 默认使用平衡权重
        class_weights = np.ones(len(class_counts)) / len(class_counts)

    class_weights = torch.FloatTensor(class_weights / class_weights.sum())
    
    return X_train, y_train, X_test, y_test, feature_cols, scaler, class_weights


def create_sequences(data, feature_cols, window_size):
    """创建时间序列数据"""
    X, y = [], []
    
    for i in range(window_size, len(data)):
        # 获取特征窗口
        features = data.iloc[i-window_size:i][feature_cols].values.flatten()
        
        # 获取目标动作 (当前时间步的动作)
        target_action = data.iloc[i]['action']
        
        
        X.append(features)
        y.append(target_action)
    
    return np.array(X), np.array(y)

# 训练函数
def train_model(X_train, y_train, X_test, y_test, input_dim, class_weights):
    """训练模型"""
    # 创建模型
    model = EnhancedTradingModel(input_dim, Config.HIDDEN_DIM, 3, Config.DROPOUT_RATE).to(Config.device)
    
    # 使用自定义损失函数
    criterion = SimpleExpertLoss(class_weights=class_weights.to(Config.device))
    optimizer = optim.AdamW(
        model.parameters(), 
        lr=Config.LEARNING_RATE, 
        weight_decay=Config.WEIGHT_DECAY
    )
    # 使用余弦退火学习率调度
    scheduler = optim.lr_scheduler.CosineAnnealingLR(
        optimizer, T_max=Config.EPOCHS, eta_min=1e-6
    )
    
    # 准备数据加载器
    train_dataset = torch.utils.data.TensorDataset(
        torch.FloatTensor(X_train), 
        torch.LongTensor(y_train)
    )
    train_loader = torch.utils.data.DataLoader(
        train_dataset, batch_size=Config.BATCH_SIZE, shuffle=True
    )
    
    test_dataset = torch.utils.data.TensorDataset(
        torch.FloatTensor(X_test), 
        torch.LongTensor(y_test)
    )
    test_loader = torch.utils.data.DataLoader(
        test_dataset, batch_size=Config.BATCH_SIZE, shuffle=False
    )
    
    # 训练循环
    best_accuracy = 0
    train_losses = []
    test_accuracies = []
    
    for epoch in range(Config.EPOCHS):
        model.train()
        total_loss = 0
        
        for batch_x, batch_y in train_loader:
            batch_x, batch_y = batch_x.to(Config.device), batch_y.to(Config.device)
            
            optimizer.zero_grad()
            outputs = model(batch_x)
            loss = criterion(outputs, batch_y)
            loss.backward()
            
            # 梯度裁剪防止梯度爆炸
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            
            optimizer.step()
            
            total_loss += loss.item()
        
        avg_loss = total_loss / len(train_loader)
        train_losses.append(avg_loss)
        
        # 评估
        model.eval()
        test_accuracy, test_report, cm = evaluate_and_plot(model, test_loader)
        test_accuracies.append(test_accuracy)
        
        # 更新学习率
        scheduler.step(test_accuracy)
        
        # 保存最佳模型
        if test_accuracy > best_accuracy:
            best_accuracy = test_accuracy
            torch.save(model.state_dict(), Config.MODEL_PATH)
            print(f"保存最佳模型，准确率: {test_accuracy:.4f}")
        
        # 打印进度
        if epoch % 10 == 0:
            current_lr = optimizer.param_groups[0]['lr']
            
            # 特别关注0类别的误判情况
            fp_0 = cm[0, 1] + cm[0, 2]  # 真实为0但预测为1或2的数量
            total_0 = cm[0].sum()  # 真实为0的总数
            fp_rate = fp_0 / total_0 if total_0 > 0 else 0
            
            print(f'Epoch {epoch}/{Config.EPOCHS}, Loss: {avg_loss:.4f}, '
                  f'Test Accuracy: {test_accuracy:.4f}, LR: {current_lr:.2e}, '
                  f'FP Rate (0->1/2): {fp_rate:.4f}')
    
    # 绘制训练曲线
    plt.figure(figsize=(12, 5))
    
    plt.subplot(1, 2, 1)
    plt.plot(train_losses)
    plt.title('Training Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    
    plt.subplot(1, 2, 2)
    plt.plot(test_accuracies)
    plt.title('Test Accuracy')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    
    plt.tight_layout()
    plt.savefig('training_curves.png')
    plt.close()
    
    # 加载最佳模型
    model.load_state_dict(torch.load(Config.MODEL_PATH))
    
    return model

# 修改评估函数，专注于关键指标
def evaluate_and_plot(model, data_loader, class_names=['Hold', 'Sell', 'Buy']):
    """评估模型并绘制混淆矩阵"""
    model.eval()
    all_preds = []
    all_targets = []
    
    with torch.no_grad():
        for batch_x, batch_y in data_loader:
            batch_x = batch_x.to(Config.device)
            outputs = model(batch_x)
            preds = torch.argmax(outputs, dim=1)
            
            all_preds.extend(preds.cpu().numpy())
            all_targets.extend(batch_y.numpy())
    
    # 计算准确率
    accuracy = accuracy_score(all_targets, all_preds)
    
    # 生成分类报告
    report = classification_report(all_targets, all_preds, target_names=class_names)
    
    # 计算混淆矩阵
    cm = confusion_matrix(all_targets, all_preds)
    
    # 绘制混淆矩阵
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=class_names,
                yticklabels=class_names)
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.title('Confusion Matrix')
    
    # 显示图像（会阻塞程序，直到关闭）
    #plt.show()
    
    return accuracy, report, cm



# 预测函数
def predict(model, data, feature_cols, scaler, window_size):
    """使用训练好的模型进行预测"""
    model.eval()
    
    # 准备输入数据
    if len(data) < window_size:
        raise ValueError(f"数据长度({len(data)})小于窗口大小({window_size})")
    
    # 获取最近window_size个时间步的数据
    recent_data = data.iloc[-window_size:][feature_cols].values
    recent_data = scaler.transform(recent_data)  # 标准化
    
    # 扁平化
    input_data = recent_data.flatten().reshape(1, -1)
    
    # 预测
    with torch.no_grad():
        input_tensor = torch.FloatTensor(input_data).to(Config.device)
        output = model(input_tensor)
        prediction = torch.argmax(output, dim=1).item()
        probabilities = F.softmax(output, dim=1).cpu().numpy()[0]
    
    return prediction, probabilities

# 主函数
def main():
    # 1. 准备数据
    ts_code = "000063.SZ" 
    file_path = fr"E:\stock\backtest\data\analyzed\5min\{ts_code}_analysis.csv"
    X_train, y_train, X_test, y_test, feature_cols, scaler, class_weights = prepare_data(file_path)
    
    input_dim = X_train.shape[1]  # 输入维度 = 窗口大小 × 特征数量
    
    print(f"类别权重: {class_weights.numpy()}")
    
    # 2. 训练模型
    model = train_model(X_train, y_train, X_test, y_test, input_dim, class_weights)
    
    # 3. 最终评估
    test_dataset = torch.utils.data.TensorDataset(
        torch.FloatTensor(X_test), 
        torch.LongTensor(y_test)
    )
    test_loader = torch.utils.data.DataLoader(
        test_dataset, batch_size=Config.BATCH_SIZE, shuffle=False
    )
    # 在main函数中调用
    accuracy, report, cm = evaluate_and_plot(model, test_loader)
    print(f"最终测试准确率: {accuracy:.4f}")
    print("分类报告:")
    print(report)
    
    # 4. 特别关注0类别的误判情况
    fp_0 = cm[0, 1] + cm[0, 2]  # 真实为0但预测为1或2的数量
    total_0 = cm[0].sum()  # 真实为0的总数
    fp_rate = fp_0 / total_0 if total_0 > 0 else 0
    print(f"0类别的误判率: {fp_rate:.4f} ({fp_0}/{total_0})")
    
    # 5. 示例预测
    # 假设我们有一个新的数据DataFrame
    # new_data = pd.read_csv("new_data.csv")
    # prediction, probs = predict(model, new_data, feature_cols, scaler, 30)
    # action_names = {0: "Hold", 1: "Sell", 2: "Buy"}
    # print(f"预测动作: {action_names[prediction]}, 概率: {probs}")

if __name__ == "__main__":
    main()