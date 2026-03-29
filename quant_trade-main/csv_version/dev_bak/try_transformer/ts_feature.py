import os
import random
import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader, WeightedRandomSampler
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix, f1_score
import warnings
warnings.filterwarnings('ignore')

# 设备配置
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# 超参数配置 (这些参数可以通过Optuna进行优化)
class Hyperparameters:
    def __init__(self):
        # 数据参数
        self.target_column = 'action'
        self.batch_size = 32
        self.train_ratio = 0.8
        self.val_ratio = 0.1
        self.test_ratio = 0.1
        self.window_size = 50  # 时间窗口大小
        self.use_weighted_sampler = True
        
        # 模型架构参数
        self.d_model = 64
        self.nhead = 8
        self.num_layers = 3
        self.dim_feedforward = 256
        self.dropout = 0.1
        self.use_cls_token = True
        self.use_time_encoding = True
        self.use_position_encoding = True
        
        # 训练参数
        self.num_epochs = 500
        self.learning_rate = 0.001
        self.weight_decay = 1e-5
        self.patience = 40  # 早停耐心值
        
        # 优化器参数
        self.optimizer_type = 'adam'  # 'adam', 'adamw', 'sgd'
        self.momentum = 0.9  # 用于SGD
        
        # 学习率调度器参数
        self.use_scheduler = True
        self.scheduler_type = 'reduce_on_plateau'  # 'step', 'cosine', 'reduce_on_plateau'
        self.step_size = 10
        self.gamma = 0.1
        self.min_lr = 1e-6
        
        # 正则化参数
        self.use_gradient_clip = True
        self.grad_clip_value = 1.0
        
        # 损失函数参数
        self.loss_type = 'cross_entropy'  # 'cross_entropy', 'focal'
        self.focal_alpha = 0.25
        self.focal_gamma = 2.0

# 设置随机种子
def set_seed(seed=42):
    torch.manual_seed(seed)
    np.random.seed(seed)
    random.seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

class TimeSeriesTransformerDataset(Dataset):
    def __init__(self, file_path, feature_columns, target_column='action', window_size=10):
        """
        时间序列Transformer数据集
        
        参数:
            file_path: CSV文件路径
            feature_columns: 特征列名列表
            target_column: 目标列名，默认为'action'
            window_size: 时间窗口大小，用于考虑历史信息
        """
        df = pd.read_csv(file_path, index_col='trade_date', parse_dates=True)
    
        # 移除不必要的列
        df = df.drop(columns=['circ_mv', 'support', 'resistance', 'ts_code'], errors='ignore')
        df['action'] = df['action'].astype(int)
        df = df.dropna()
        self.data = df
        self.features = self.data[feature_columns].values
        self.targets = self.data[target_column].values
        self.window_size = window_size
        
        # 标准化特征
        self.scaler = StandardScaler()
        self.features = self.scaler.fit_transform(self.features)
        
    def __len__(self):
        return len(self.data) - self.window_size
    
    def __getitem__(self, idx):
        # 获取当前时间步及之前window_size个时间步的数据
        start_idx = idx
        end_idx = idx + self.window_size
        sequence_features = self.features[start_idx:end_idx]
        target = self.targets[end_idx - 1]  # 使用窗口最后一个时间步的目标
        
        return (
            torch.tensor(sequence_features, dtype=torch.float32),
            torch.tensor(target, dtype=torch.long)
        )

class TimeSeriesTransformer(nn.Module):
    def __init__(self, num_features, num_classes, d_model=64, nhead=8, 
                 num_layers=3, dim_feedforward=256, dropout=0.1, 
                 use_cls_token=True, use_time_encoding=True, use_position_encoding=True):
        """
        时间序列Transformer模型
        
        参数:
            num_features: 特征数量
            num_classes: 类别数量
            d_model: 模型维度
            nhead: 注意力头数
            num_layers: Transformer层数
            dim_feedforward: 前馈网络维度
            dropout: Dropout率
            use_cls_token: 是否使用CLS token
            use_time_encoding: 是否使用时间编码
            use_position_encoding: 是否使用位置编码
        """
        super(TimeSeriesTransformer, self).__init__()
        self.num_features = num_features
        self.d_model = d_model
        self.use_cls_token = use_cls_token
        self.use_time_encoding = use_time_encoding
        self.use_position_encoding = use_position_encoding
        
        # 特征嵌入层 - 将每个特征映射到d_model维度
        self.feature_embedding = nn.Linear(num_features, d_model)
        
        # 位置编码
        if use_position_encoding:
            self.position_encoding = nn.Parameter(torch.zeros(1, 1000, d_model))  # 支持最大1000个时间步
        
        # 时间位置编码
        if use_time_encoding:
            self.time_encoding = nn.Parameter(torch.zeros(1, 1000, d_model))
        
        # Transformer编码器
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model, 
            nhead=nhead, 
            dim_feedforward=dim_feedforward, 
            dropout=dropout,
            batch_first=True
        )
        self.transformer_encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        
        # CLS token
        if use_cls_token:
            self.cls_token = nn.Parameter(torch.zeros(1, 1, d_model))
        
        # 分类器
        self.classifier = nn.Sequential(
            nn.Linear(d_model, 128),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(64, num_classes)
        )
        
    def forward(self, x):
        batch_size, seq_len, num_features = x.shape
        
        # 嵌入每个时间步的特征
        x = self.feature_embedding(x)  # (batch_size, seq_len, d_model)
        
        # 添加位置编码
        if self.use_position_encoding:
            x = x + self.position_encoding[:, :seq_len, :]
        
        # 添加时间编码
        if self.use_time_encoding:
            x = x + self.time_encoding[:, :seq_len, :]
        
        # 添加CLS token
        if self.use_cls_token:
            cls_tokens = self.cls_token.expand(batch_size, -1, -1)
            x = torch.cat((cls_tokens, x), dim=1)  # (batch_size, seq_len+1, d_model)
            seq_len = seq_len + 1
        
        # 通过Transformer编码器
        x = self.transformer_encoder(x)  # (batch_size, seq_len, d_model)
        
        # 使用CLS token或最后一个时间步的输出进行分类
        if self.use_cls_token:
            output = x[:, 0, :]  # CLS token
        else:
            output = x[:, -1, :]  # 最后一个时间步
        
        # 分类
        return self.classifier(output)

def create_optimizer(model, hp):
    """创建优化器"""
    if hp.optimizer_type == 'adam':
        return torch.optim.Adam(
            model.parameters(), 
            lr=hp.learning_rate, 
            weight_decay=hp.weight_decay
        )
    elif hp.optimizer_type == 'adamw':
        return torch.optim.AdamW(
            model.parameters(), 
            lr=hp.learning_rate, 
            weight_decay=hp.weight_decay
        )
    elif hp.optimizer_type == 'sgd':
        return torch.optim.SGD(
            model.parameters(), 
            lr=hp.learning_rate, 
            momentum=hp.momentum,
            weight_decay=hp.weight_decay
        )
    else:
        raise ValueError(f"不支持的优化器类型: {hp.optimizer_type}")

def create_scheduler(optimizer, hp):
    """创建学习率调度器"""
    if not hp.use_scheduler:
        return None
    
    if hp.scheduler_type == 'step':
        return torch.optim.lr_scheduler.StepLR(
            optimizer, 
            step_size=hp.step_size, 
            gamma=hp.gamma
        )
    elif hp.scheduler_type == 'cosine':
        return torch.optim.lr_scheduler.CosineAnnealingLR(
            optimizer, 
            T_max=hp.num_epochs
        )
    elif hp.scheduler_type == 'reduce_on_plateau':
        return torch.optim.lr_scheduler.ReduceLROnPlateau(
            optimizer, 
            mode='max',  # 监控指标是准确率，所以是max
            patience=hp.patience // 2,  # 通常早停耐心值的一半
            factor=hp.gamma,
            min_lr=hp.min_lr
        )
    else:
        raise ValueError(f"不支持的调度器类型: {hp.scheduler_type}")

def create_loss_function(hp, class_weights=None):
    """创建损失函数"""
    if hp.loss_type == 'cross_entropy':
        if class_weights is not None:
            return nn.CrossEntropyLoss(weight=class_weights.to(device))
        else:
            return nn.CrossEntropyLoss()
    elif hp.loss_type == 'focal':
        # 实现Focal Loss
        class FocalLoss(nn.Module):
            def __init__(self, alpha=0.25, gamma=2.0, reduction='mean'):
                super(FocalLoss, self).__init__()
                self.alpha = alpha
                self.gamma = gamma
                self.reduction = reduction
            
            def forward(self, inputs, targets):
                BCE_loss = nn.CrossEntropyLoss(reduction='none')(inputs, targets)
                pt = torch.exp(-BCE_loss)
                F_loss = self.alpha * (1-pt)**self.gamma * BCE_loss
                
                if self.reduction == 'mean':
                    return torch.mean(F_loss)
                elif self.reduction == 'sum':
                    return torch.sum(F_loss)
                else:
                    return F_loss
        
        return FocalLoss(alpha=hp.focal_alpha, gamma=hp.focal_gamma)
    else:
        raise ValueError(f"不支持的损失函数类型: {hp.loss_type}")

def train_model(model, train_loader, val_loader, hp, class_weights=None):
    """训练模型"""
    # 创建优化器和损失函数
    optimizer = create_optimizer(model, hp)
    criterion = create_loss_function(hp, class_weights)
    scheduler = create_scheduler(optimizer, hp)
    
    # 早停参数
    best_val_acc = 0.0
    patience_counter = 0
    best_model_state = None
    
    # 训练历史
    history = {
        'train_loss': [],
        'val_loss': [],
        'val_acc': [],
        'val_f1': []
    }
    
    for epoch in range(hp.num_epochs):
        # 训练阶段
        model.train()
        train_loss = 0.0
        
        for batch_idx, (data, target) in enumerate(train_loader):
            data, target = data.to(device), target.to(device)
            
            optimizer.zero_grad()
            output = model(data)
            loss = criterion(output, target)
            loss.backward()
            
            # 梯度裁剪
            if hp.use_gradient_clip:
                torch.nn.utils.clip_grad_norm_(model.parameters(), hp.grad_clip_value)
            
            optimizer.step()
            
            train_loss += loss.item()
        
        # 验证阶段
        val_loss, val_acc, val_f1 = evaluate_model(model, val_loader, criterion)
        
        # 记录历史
        history['train_loss'].append(train_loss / len(train_loader))
        history['val_loss'].append(val_loss)
        history['val_acc'].append(val_acc)
        history['val_f1'].append(val_f1)
        
        # 学习率调度
        if scheduler is not None:
            if isinstance(scheduler, torch.optim.lr_scheduler.ReduceLROnPlateau):
                scheduler.step(val_acc)
            else:
                scheduler.step()
        
        # 早停检查
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            patience_counter = 0
            best_model_state = model.state_dict().copy()
            print(f'Epoch {epoch+1}: 新的最佳验证准确率: {val_acc:.4f}')
        else:
            patience_counter += 1
            if patience_counter >= hp.patience:
                print(f'早停在第 {epoch+1} 轮，最佳验证准确率: {best_val_acc:.4f}')
                break
        
        print(f'Epoch {epoch+1}/{hp.num_epochs}, Train Loss: {train_loss/len(train_loader):.4f}, '
              f'Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.4f}, Val F1: {val_f1:.4f}')
    
    # 恢复最佳模型
    if best_model_state is not None:
        model.load_state_dict(best_model_state)
    
    return model, history

def evaluate_model(model, data_loader, criterion=None):
    """评估模型"""
    model.eval()
    total_loss = 0.0
    correct = 0
    total = 0
    all_predictions = []
    all_targets = []
    
    with torch.no_grad():
        for data, target in data_loader:
            data, target = data.to(device), target.to(device)
            outputs = model(data)
            
            if criterion is not None:
                loss = criterion(outputs, target)
                total_loss += loss.item()
            
            _, predicted = torch.max(outputs.data, 1)
            total += target.size(0)
            correct += (predicted == target).sum().item()
            
            all_predictions.extend(predicted.cpu().numpy())
            all_targets.extend(target.cpu().numpy())
    
    accuracy = correct / total
    avg_loss = total_loss / len(data_loader) if criterion is not None else 0.0
    
    # 计算F1分数
    f1 = f1_score(all_targets, all_predictions, average='weighted')
    
    return avg_loss, accuracy, f1

def main(hp):
    # 设置随机种子
    set_seed()
    
    # 获取所有CSV文件
    ts_code = "000063.SZ" 
    #file_path = fr"E:\stock\backtest\data\analyzed\5min\{ts_code}_analysis.csv"
    data_dir = fr"E:\stock\backtest\data\analyzed\5min"  # 替换为你的CSV文件目录
    csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    if not csv_files:
        print("目录中没有找到CSV文件")
        return
    
    # 随机选择一个文件
    selected_file = random.choice(csv_files)
    file_path = os.path.join(data_dir, selected_file)
    print(f"随机选择的文件: {selected_file}")
    
    df = pd.read_csv(file_path, index_col='trade_date', parse_dates=True)
    
    # 移除不必要的列
    df = df.drop(columns=['circ_mv', 'support', 'resistance', 'ts_code'], errors='ignore')
    df['action'] = df['action'].astype(int)
    df = df.dropna()
    # 读取CSV文件的第一行来获取列名
    df_sample = df
    feature_columns = [col for col in df_sample.columns if col != hp.target_column]
    num_features = len(feature_columns)
    
    # 创建数据集
    dataset = TimeSeriesTransformerDataset(file_path, feature_columns, hp.target_column, hp.window_size)
    
    # 计算类别权重
    class_counts = np.bincount(dataset.targets[hp.window_size:])  # 跳过前window_size个样本
    class_weights = 1.0 / class_counts
    class_weights = torch.tensor(class_weights, dtype=torch.float32)
    num_classes = len(class_weights)
    print(f"类别权重: {class_weights}")
    
    # 划分数据集
    dataset_size = len(dataset)
    train_size = int(hp.train_ratio * dataset_size)
    val_size = int(hp.val_ratio * dataset_size)
    test_size = dataset_size - train_size - val_size
    
    train_dataset, val_dataset, test_dataset = torch.utils.data.random_split(
        dataset, [train_size, val_size, test_size]
    )
    
    # 创建加权采样器以处理类别不平衡
    if hp.use_weighted_sampler:
        train_targets = [dataset.targets[i + hp.window_size] for i in train_dataset.indices]
        class_weights_train = class_weights[train_targets]
        sampler = WeightedRandomSampler(class_weights_train, len(train_targets), replacement=True)
    else:
        sampler = None
    
    # 创建数据加载器
    train_loader = DataLoader(
        train_dataset, 
        batch_size=hp.batch_size, 
        sampler=sampler,
        shuffle=sampler is None
    )
    val_loader = DataLoader(val_dataset, batch_size=hp.batch_size, shuffle=False)
    test_loader = DataLoader(test_dataset, batch_size=hp.batch_size, shuffle=False)
    
    # 初始化模型
    model = TimeSeriesTransformer(
        num_features=num_features,
        num_classes=num_classes,
        d_model=hp.d_model,
        nhead=hp.nhead,
        num_layers=hp.num_layers,
        dim_feedforward=hp.dim_feedforward,
        dropout=hp.dropout,
        use_cls_token=hp.use_cls_token,
        use_time_encoding=hp.use_time_encoding,
        use_position_encoding=hp.use_position_encoding
    ).to(device)
    
    # 训练模型
    print("开始训练模型...")
    model, history = train_model(model, train_loader, val_loader, hp, class_weights)
    
    # 在测试集上评估模型
    print("在测试集上评估模型...")
    test_loss, test_acc, test_f1 = evaluate_model(model, test_loader)
    print(f"测试集结果 - 损失: {test_loss:.4f}, 准确率: {test_acc:.4f}, F1分数: {test_f1:.4f}")
    
    # 输出详细分类报告
    predictions, targets = [], []
    model.eval()
    with torch.no_grad():
        for data, target in test_loader:
            data = data.to(device)
            outputs = model(data)
            _, predicted = torch.max(outputs.data, 1)
            predictions.extend(predicted.cpu().numpy())
            targets.extend(target.numpy())
    
    print("\n分类报告:")
    print(classification_report(targets, predictions, target_names=[f'Class {i}' for i in range(num_classes)]))
    
    print("混淆矩阵:")
    print(confusion_matrix(targets, predictions))
    
    return test_acc, test_f1, history

if __name__ == "__main__":
    # 初始化超参数
    hp = Hyperparameters()
    
    # 运行主函数
    test_acc, test_f1, history = main(hp)
    
    # 输出最终结果
    print(f"\n最终测试准确率: {test_acc:.4f}")
    print(f"最终测试F1分数: {test_f1:.4f}")