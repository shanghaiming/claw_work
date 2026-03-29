import os
import random
import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader, WeightedRandomSampler
from sklearn.metrics import classification_report, confusion_matrix, f1_score, roc_curve, auc
from sklearn.preprocessing import label_binarize
import optuna
import logging
from datetime import datetime
import json
import warnings
import argparse
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict
import torch.nn.functional as F
warnings.filterwarnings('ignore')

# 添加命令行参数解析
def parse_args():
    parser = argparse.ArgumentParser(description='Stock Prediction with Transformer')
    parser.add_argument('--skip-optuna', action='store_true', 
                       help='Skip hyperparameter optimization and use pre-defined best parameters')
    parser.add_argument('--trials', type=int, default=500,
                       help='Number of Optuna trials to run (default: 500)')
    parser.add_argument('--data-dir', type=str, default=r"E:\stock\backtest\data\analyzed\5min",
                       help='Directory containing stock data CSV files')
    parser.add_argument('--save-dir', type=str, default="saved_models",
                       help='Directory to save models and results')
    return parser.parse_args()

# 设备配置
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# 超参数配置
class Hyperparameters:
    def __init__(self):
        # 数据参数
        self.target_column = 'action'
        self.batch_size = 32
        self.train_ratio = 0.8
        self.test_ratio = 0.2
        self.window_size = 50
        
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
        self.num_epochs = 100
        self.learning_rate = 0.001
        self.weight_decay = 1e-5
        self.patience = 20
        
        # 优化器参数
        self.optimizer_type = 'adam'
        self.momentum = 0.9
        
        # 学习率调度器参数
        self.use_scheduler = True
        self.scheduler_type = 'reduce_on_plateau'
        self.step_size = 10
        self.gamma = 0.5
        self.min_lr = 1e-6
        
        # 正则化参数
        self.use_gradient_clip = True
        self.grad_clip_value = 1.0
        
        # 损失函数参数
        self.loss_type = 'focal'  # 'cross_entropy' or 'focal'
        self.focal_alpha = 0.1
        self.focal_gamma = 3
        
        # 早期淘汰参数
        self.early_rejection_threshold = 0.001
        self.min_epochs_before_reject = 5
        
        # 实例标准化分组配置 - 您需要根据实际特征修改这里
        self.feature_groups = {
            "price_group": ['open', 'high', 'low', 'close', 'ma5',
                            'ma8', 'ma13', 'ma21', 'ma34', 'ma55',
                            'tsma5', 'tsma8', 'tsma13', 'sma', 'std', 'upper', 'lower', 'target'],
            "wr": ['wr5', 'wr55'],
            "macd": ['diff', 'dea', 'macd']
            # 根据需要添加更多分组...
        }

# 设置随机种子
def set_seed(seed=42):
    torch.manual_seed(seed)
    np.random.seed(seed)
    random.seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

# 实例标准化函数
def instance_normalization(window, feature_names, feature_groups):
    """
    对窗口数据进行分层实例标准化
    
    参数:
        window: 形状为 (window_size, num_features) 的数组
        feature_names: 特征名称列表
        feature_groups: 字典，键是组名，值是特征名称列表
        
    返回:
        标准化后的窗口数据
    """
    normalized_window = window.copy().astype(np.float32)
    
    # 创建特征名称到索引的映射
    feature_to_idx = {name: idx for idx, name in enumerate(feature_names)}
    
    # 处理每个分组
    for group_name, group_features in feature_groups.items():
        # 获取该组特征的索引
        group_indices = []
        for feature in group_features:
            if feature in feature_to_idx:
                group_indices.append(feature_to_idx[feature])
        
        if not group_indices:  # 跳过空组
            continue
            
        # 提取该组特征
        group_data = window[:, group_indices]
        
        # 计算该组特征的均值和标准差
        mean = np.mean(group_data, axis=0, keepdims=True)
        std = np.std(group_data, axis=0, keepdims=True)
        
        # 避免除零
        std = np.where(std < 1e-8, 1.0, std)
        
        # 标准化该组特征
        normalized_group = (group_data - mean) / std
        
        # 将标准化后的特征放回原位置
        normalized_window[:, group_indices] = normalized_group
    
    # 处理未分组的特征 - 每个特征单独标准化
    all_grouped_indices = []
    for group_features in feature_groups.values():
        for feature in group_features:
            if feature in feature_to_idx:
                all_grouped_indices.append(feature_to_idx[feature])
    
    # 找出未分组的特征索引
    ungrouped_indices = [i for i in range(len(feature_names)) if i not in all_grouped_indices]
    
    # 对每个未分组的特征单独标准化
    for idx in ungrouped_indices:
        feature_data = window[:, idx]
        mean = np.mean(feature_data)
        std = np.std(feature_data)
        std = 1.0 if std < 1e-8 else std
        normalized_window[:, idx] = (feature_data - mean) / std
    
    return normalized_window

# 数据集类
class StockDataset(Dataset):
    def __init__(self, features, targets, feature_names, window_size=50, feature_groups=None):
        self.features = features.astype(np.float32)
        self.targets = targets
        self.window_size = window_size
        self.feature_groups = feature_groups
        self.feature_names = feature_names  # 保存特征名称
        
    def __len__(self):
        return len(self.features) - self.window_size
    
    def __getitem__(self, idx):
        # 获取原始窗口数据
        sequence_features = self.features[idx:idx+self.window_size]
        
        # 应用实例标准化
        if self.feature_groups is not None:
            sequence_features = instance_normalization(
                sequence_features, self.feature_names, self.feature_groups
            )
        
        target = self.targets[idx+self.window_size-1]
        return (
            torch.tensor(sequence_features, dtype=torch.float32),
            torch.tensor(target, dtype=torch.long)
        )

# Transformer模型
class TimeSeriesTransformer(nn.Module):
    def __init__(self, num_features, num_classes, d_model=64, nhead=8, 
                 num_layers=3, dim_feedforward=256, dropout=0.1, 
                 use_cls_token=True, use_time_encoding=True, use_position_encoding=True):
        super(TimeSeriesTransformer, self).__init__()
        self.num_features = num_features
        self.d_model = d_model
        self.use_cls_token = use_cls_token
        self.use_time_encoding = use_time_encoding
        self.use_position_encoding = use_position_encoding
        
        # 特征嵌入层
        self.feature_embedding = nn.Linear(num_features, d_model)
        
        # 位置编码
        if use_position_encoding:
            self.position_encoding = nn.Parameter(torch.zeros(1, 1000, d_model))
        
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
        x = self.feature_embedding(x)
        
        # 添加位置编码
        if self.use_position_encoding:
            x = x + self.position_encoding[:, :seq_len, :]
        
        # 添加时间编码
        if self.use_time_encoding:
            x = x + self.time_encoding[:, :seq_len, :]
        
        # 添加CLS token
        if self.use_cls_token:
            cls_tokens = self.cls_token.expand(batch_size, -1, -1)
            x = torch.cat((cls_tokens, x), dim=1)
            seq_len = seq_len + 1
        
        # 通过Transformer编码器
        x = self.transformer_encoder(x)
        
        # 使用CLS token或最后一个时间步的输出进行分类
        if self.use_cls_token:
            output = x[:, 0, :]
        else:
            output = x[:, -1, :]
        
        # 分类
        return self.classifier(output)

# 创建优化器
def create_optimizer(model, hp):
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
        raise ValueError(f"Unsupported optimizer type: {hp.optimizer_type}")

# 创建学习率调度器
def create_scheduler(optimizer, hp):
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
            mode='max',
            patience=hp.patience // 2,
            factor=hp.gamma,
            min_lr=hp.min_lr
        )
    else:
        raise ValueError(f"Unsupported scheduler type: {hp.scheduler_type}")

# 创建损失函数
def create_loss_function(hp, class_weights=None):
    if hp.loss_type == 'cross_entropy':
        if class_weights is not None:
            return nn.CrossEntropyLoss(weight=class_weights.to(device))
        else:
            return nn.CrossEntropyLoss()
    elif hp.loss_type == 'focal':
        # 确保类别权重在正确的设备上
        if class_weights is not None:
            class_weights = class_weights.to(device)
        
        class FocalLoss(nn.Module):
            def __init__(self, alpha=0.25, gamma=2.0, reduction='mean', weight=None):
                super(FocalLoss, self).__init__()
                self.alpha = alpha
                self.gamma = gamma
                self.reduction = reduction
                # 使用 register_buffer 确保权重与模型在同一设备上
                if weight is not None:
                    self.register_buffer('weight', weight)
                else:
                    self.weight = None
            
            def forward(self, inputs, targets):
                # 计算基础的交叉熵损失
                ce_loss = F.cross_entropy(inputs, targets, reduction='none')
                
                # 计算概率
                pt = torch.exp(-ce_loss)
                
                # 计算Focal Loss
                focal_loss = self.alpha * (1-pt)**self.gamma * ce_loss
                
                # 应用类别权重
                if self.weight is not None:
                    weight_tensor = self.weight[targets]
                    focal_loss = focal_loss * weight_tensor
                
                if self.reduction == 'mean':
                    return torch.mean(focal_loss)
                elif self.reduction == 'sum':
                    return torch.sum(focal_loss)
                else:
                    return focal_loss
        
        # 创建Focal Loss实例，传入类别权重
        return FocalLoss(alpha=hp.focal_alpha, gamma=hp.focal_gamma, weight=class_weights)
    else:
        raise ValueError(f"Unsupported loss type: {hp.loss_type}")
# 评估模型（返回概率）
def evaluate_model_with_probs(model, data_loader, criterion=None):
    model.eval()
    total_loss = 0.0
    correct = 0
    total = 0
    all_predictions = []
    all_targets = []
    all_probabilities = []
    
    with torch.no_grad():
        for data, target in data_loader:
            data, target = data.to(device), target.to(device)
            outputs = model(data)
            probabilities = torch.softmax(outputs, dim=1)
            
            if criterion is not None:
                loss = criterion(outputs, target)
                total_loss += loss.item()
            
            _, predicted = torch.max(outputs.data, 1)
            total += target.size(0)
            correct += (predicted == target).sum().item()
            
            all_predictions.extend(predicted.cpu().numpy())
            all_targets.extend(target.cpu().numpy())
            all_probabilities.extend(probabilities.cpu().numpy())
    
    accuracy = correct / total
    avg_loss = total_loss / len(data_loader) if criterion is not None else 0.0
    
    f1 = f1_score(all_targets, all_predictions, average='weighted')
    
    return avg_loss, accuracy, f1, all_predictions, all_targets, all_probabilities

def write_normalization_debug_info(file_path, original_data, normalized_data, feature_names, window_index):
    """
    将标准化前后的数据写入文件以便分析
    
    参数:
        file_path: 输出文件路径
        original_data: 原始窗口数据
        normalized_data: 标准化后的窗口数据
        feature_names: 特征名称列表
        window_index: 窗口索引
    """
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(f"=== 窗口 {window_index} ===\n")
        f.write("原始数据:\n")
        for i, feature_name in enumerate(feature_names):
            feature_values = original_data[:, i]
            f.write(f"  {feature_name}: {feature_values}\n")
            f.write(f"    均值={feature_values.mean():.6f}, 标准差={feature_values.std():.6f}\n")
        
        f.write("\n标准化后数据:\n")
        for i, feature_name in enumerate(feature_names):
            feature_values = normalized_data[:, i]
            f.write(f"  {feature_name}: {feature_values}\n")
            f.write(f"    均值={feature_values.mean():.6f}, 标准差={feature_values.std():.6f}\n")
        
        f.write("\n" + "="*50 + "\n\n")



# 准备单只股票数据
def prepare_single_stock_data(file_path, hp, debug_output_path=None):
    df = pd.read_csv(file_path, index_col='trade_date', parse_dates=True)
    df = df.drop(columns=['circ_mv', 'support', 'resistance', 'ts_code'], errors='ignore')
    df['action'] = df['action'].astype(int)
    df = df.dropna()
    
    feature_columns = [col for col in df.columns if col != hp.target_column]
    features = df[feature_columns].values
    targets = df[hp.target_column].values
    
    # 划分训练集和测试集
    train_size = int(len(features) * hp.train_ratio)
    
    train_features = features[:train_size]
    test_features = features[train_size:]
    train_targets = targets[:train_size]
    test_targets = targets[train_size:]
    
    # 创建数据集
    train_dataset = StockDataset(train_features, train_targets, feature_columns, hp.window_size, hp.feature_groups)
    test_dataset = StockDataset(test_features, test_targets, feature_columns, hp.window_size, hp.feature_groups)
    
    # 如果提供了调试输出路径，则写入标准化前后的数据
    if debug_output_path:
        # 清空或创建输出文件
        with open(debug_output_path, 'w', encoding='utf-8') as f:
            f.write("实例标准化调试信息\n")
            f.write(f"数据文件: {file_path}\n")
            f.write(f"特征分组: {hp.feature_groups}\n")
            f.write(f"窗口大小: {hp.window_size}\n")
            f.write("="*50 + "\n\n")
        
        # 写入前5个窗口的标准化信息
        for i in range(min(5, len(train_dataset))):
            # 获取原始窗口数据
            original_window = train_features[i:i+hp.window_size]
            
            # 应用实例标准化
            normalized_window = instance_normalization(original_window, feature_columns, hp.feature_groups)
            
            # 写入文件
            write_normalization_debug_info(debug_output_path, original_window, normalized_window, feature_columns, i)
    
    # 计算类别权重
    class_counts = np.bincount(train_targets[hp.window_size:])
    #class_weights = 1.0 / class_counts
    class_weights = np.array([0.01, 4.0, 4.0])  # 自定义权重
    # 归一化权重
    class_weights = class_weights / class_weights.sum() * len(class_weights)
    class_weights = torch.tensor(class_weights, dtype=torch.float32)
    
    # 创建数据加载器
    train_loader = DataLoader(train_dataset, batch_size=hp.batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=hp.batch_size, shuffle=False)
    
    return train_loader, test_loader, class_weights, len(feature_columns), len(class_counts), feature_columns

# 准备多股票数据
def prepare_multi_stock_data(file_paths, hp):
    all_train_features = []
    all_train_targets = []
    all_test_features = []
    all_test_targets = []
    
    for file_path in file_paths:
        df = pd.read_csv(file_path, index_col='trade_date', parse_dates=True)
        df = df.drop(columns=['circ_mv', 'support', 'resistance', 'ts_code'], errors='ignore')
        df['action'] = df['action'].astype(int)
        df = df.dropna()
        
        stock_code = os.path.basename(file_path).split('_')[0]
        feature_columns = [col for col in df.columns if col != hp.target_column]
        features = df[feature_columns].values
        targets = df[hp.target_column].values
        
        # 划分训练集和测试集
        train_size = int(len(features) * hp.train_ratio)
        
        train_features = features[:train_size]
        test_features = features[train_size:]
        train_targets = targets[:train_size]
        test_targets = targets[train_size:]
        
        # 收集所有数据
        all_train_features.append(train_features)
        all_train_targets.append(train_targets)
        all_test_features.append(test_features)
        all_test_targets.append(test_targets)
    
    # 合并所有数据
    train_features = np.vstack(all_train_features)
    train_targets = np.hstack(all_train_targets)
    test_features = np.vstack(all_test_features)
    test_targets = np.hstack(all_test_targets)
    
    # 创建数据集 - 传入特征分组
    train_dataset = StockDataset(
        train_features, 
        train_targets, 
        feature_columns,  # 特征名称列表
        hp.window_size,   # 窗口大小
        hp.feature_groups # 特征分组
    )
    test_dataset = StockDataset(
        test_features, 
        test_targets, 
        feature_columns,  # 特征名称列表
        hp.window_size,   # 窗口大小
        hp.feature_groups # 特征分组
    )
    
    # 计算类别权重
    class_counts = np.bincount(train_targets[hp.window_size:])
    #class_weights = 1.0 / class_counts
    class_weights = np.array([1.0, 4.0, 4.0])  # 自定义权重
    class_weights = torch.tensor(class_weights, dtype=torch.float32)
    
    # 创建数据加载器 - 使用多进程加速
    train_loader = DataLoader(
        train_dataset, 
        batch_size=hp.batch_size, 
        shuffle=True,
        num_workers=8,  # 使用更多工作进程处理更大的数据集
        pin_memory=True
    )
    test_loader = DataLoader(
        test_dataset, 
        batch_size=hp.batch_size, 
        shuffle=False,
        num_workers=8,
        pin_memory=True
    )
    
    return train_loader, test_loader, class_weights, len(feature_columns), len(class_weights)

# 分析学习曲线，判断是否应该早期淘汰
def should_reject_early(history, epoch, hp):
    """基于学习曲线判断是否应该早期淘汰"""
    if epoch < hp.min_epochs_before_reject or epoch > 10:
        return False
    
    train_losses = history['train_loss']
    
    # 计算最近几个epoch的训练损失下降率
    recent_epochs = min(5, len(train_losses) - 1)
    if recent_epochs < 2:
        return False
    
    recent_losses = train_losses[-recent_epochs:]
    
    # 计算平均下降率
    decreases = []
    for i in range(1, len(recent_losses)):
        decrease = recent_losses[i-1] - recent_losses[i]
        decrease_ratio = decrease / recent_losses[i-1] if recent_losses[i-1] > 0 else 0
        decreases.append(decrease_ratio)
    
    avg_decrease = np.mean(decreases) if decreases else 0
    
    # 如果平均下降率低于阈值，考虑淘汰
    if avg_decrease < hp.early_rejection_threshold:
        return True
    
    return False

# 训练模型（带早期淘汰）
def train_model_with_early_rejection(model, train_loader, val_loader, hp, class_weights=None, logger=None):
    optimizer = create_optimizer(model, hp)
    criterion = create_loss_function(hp, class_weights)
    scheduler = create_scheduler(optimizer, hp)
    
    best_val_acc = 0.0
    patience_counter = 0
    best_val_loss = 100
    best_model_state = None
    
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
            
            if hp.use_gradient_clip:
                torch.nn.utils.clip_grad_norm_(model.parameters(), hp.grad_clip_value)
            
            optimizer.step()
            
            train_loss += loss.item()
        
        # 验证阶段
        val_loss, val_acc, val_f1, _, _, _ = evaluate_model_with_probs(model, val_loader, criterion)
        
        # 记录历史
        history['train_loss'].append(train_loss / len(train_loader))
        history['val_loss'].append(val_loss)
        history['val_acc'].append(val_acc)
        history['val_f1'].append(val_f1)
        
        # 记录日志
        if logger:
            logger.info(f"Epoch {epoch+1}/{hp.num_epochs}, Train Loss: {train_loss/len(train_loader):.4f}, "
                       f"Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.4f}, Val F1: {val_f1:.4f}")
        
        # 学习率调度
        if scheduler is not None:
            if isinstance(scheduler, torch.optim.lr_scheduler.ReduceLROnPlateau):
                scheduler.step(val_acc)
            else:
                scheduler.step()
        
        # 检查是否应该早期淘汰
        if should_reject_early(history, epoch, hp):
            if logger:
                logger.info(f"Early rejection at epoch {epoch+1} due to poor learning curve")
            return model, history, True  # 第三个参数表示是否被淘汰
        
        # 早停检查
        if (val_acc > best_val_acc and val_loss < best_val_loss*1.1):
            best_val_acc = val_acc
            best_val_loss = val_loss
            patience_counter = 0
            best_model_state = model.state_dict().copy()
            if logger:
                logger.info(f"Epoch {epoch+1}: New best validation accuracy: {val_acc:.4f}")
        else:
            patience_counter += 1
            if patience_counter >= hp.patience:
                if logger:
                    logger.info(f"Early stopping at epoch {epoch+1}, best validation accuracy: {best_val_acc:.4f}")
                break
    
    # 恢复最佳模型
    if best_model_state is not None:
        model.load_state_dict(best_model_state)
    
    return model, history, False

# 设置日志记录
def setup_logging(log_dir="logs"):
    """设置日志记录，包括重定向 Optuna 的日志"""
    os.makedirs(log_dir, exist_ok=True)
    
    # 生成日志文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"optuna_tuning_{timestamp}.log")
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # 清除现有的处理器
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 创建格式化器
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # 创建文件处理器
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    
    # 添加处理器到根日志记录器
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # 配置 Optuna 的日志记录器
    optuna_logger = logging.getLogger('optuna')
    optuna_logger.setLevel(logging.INFO)
    optuna_logger.addHandler(file_handler)
    optuna_logger.addHandler(console_handler)
    optuna_logger.propagate = False  # 防止重复记录
    
    return logging.getLogger(__name__)

# 保存试验结果到文件
def save_trial_results(study, filename="optuna_trials.csv"):
    """保存所有试验结果到CSV文件"""
    trials_df = study.trials_dataframe()
    trials_df.to_csv(filename, index=False)
    return trials_df

# 打印前N个最佳试验
def print_top_trials(study, n=10, logger=None):
    """打印前N个最佳试验的结果"""
    trials = study.trials
    best_trials = sorted(trials, key=lambda x: x.value if x.value is not None else -float('inf'), reverse=True)[:n]
    
    if logger:
        logger.info(f"\nTop {n} trials:")
        for i, trial in enumerate(best_trials):
            logger.info(f"Trial #{i+1}: Value = {trial.value:.4f}")
            logger.info(f"  Params: {trial.params}")
            for attr_name, attr_value in trial.user_attrs.items():
                logger.info(f"  {attr_name}: {attr_value}")
    else:
        print(f"\nTop {n} trials:")
        for i, trial in enumerate(best_trials):
            print(f"Trial #{i+1}: Value = {trial.value:.4f}")
            print(f"  Params: {trial.params}")
            for attr_name, attr_value in trial.user_attrs.items():
                print(f"  {attr_name}: {attr_value}")

# 保存模型
def save_model(model, save_dir, model_name):
    """保存模型状态字典"""
    os.makedirs(save_dir, exist_ok=True)
    model_path = os.path.join(save_dir, f"{model_name}.pth")
    torch.save(model.state_dict(), model_path)
    return model_path

# 绘制ROC曲线
def plot_roc_auc(y_true, y_prob, class_names, save_dir, model_name):
    """绘制多分类ROC曲线并计算AUC"""
    # 将标签二值化
    y_true_bin = label_binarize(y_true, classes=range(len(class_names)))
    
    # 计算每个类别的ROC曲线和AUC
    fpr = dict()
    tpr = dict()
    roc_auc = dict()
    
    for i in range(len(class_names)):
        fpr[i], tpr[i], _ = roc_curve(y_true_bin[:, i], y_prob[:, i])
        roc_auc[i] = auc(fpr[i], tpr[i])
    
    # 计算微平均ROC曲线和AUC
    fpr["micro"], tpr["micro"], _ = roc_curve(y_true_bin.ravel(), y_prob.ravel())
    roc_auc["micro"] = auc(fpr["micro"], tpr["micro"])
    
    # 绘制所有ROC曲线
    plt.figure(figsize=(10, 8))
    
    colors = ['red', 'green', 'blue', 'orange', 'purple'][:len(class_names)]
    
    for i, color in zip(range(len(class_names)), colors):
        plt.plot(fpr[i], tpr[i], color=color, lw=2,
                label=f'ROC curve of class {class_names[i]} (AUC = {roc_auc[i]:.2f})')
    
    # 绘制微平均ROC曲线
    plt.plot(fpr["micro"], tpr["micro"],
             label=f'micro-average ROC curve (AUC = {roc_auc["micro"]:.2f})',
             color='deeppink', linestyle=':', linewidth=4)
    
    plt.plot([0, 1], [0, 1], 'k--', lw=2)
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Multi-class ROC Curve')
    plt.legend(loc="lower right")
    
    # 保存图像
    roc_path = os.path.join(save_dir, f"{model_name}_roc_auc.png")
    plt.savefig(roc_path)
    plt.close()
    
    return roc_auc, roc_path

# 绘制概率热力图
def plot_probability_heatmap(y_true, y_pred, y_prob, class_names, save_dir, model_name):
    """绘制预测概率的热力图"""
    n_classes = len(class_names)
    
    # 创建子图
    fig, axes = plt.subplots(n_classes, n_classes, figsize=(15, 12))
    
    for true_class in range(n_classes):
        for pred_class in range(n_classes):
            # 获取真实类别为true_class且预测类别为pred_class的样本
            mask = (y_true == true_class) & (y_pred == pred_class)
            probs = y_prob[mask, pred_class]
            
            if len(probs) > 0:
                # 绘制箱线图
                axes[true_class, pred_class].boxplot(probs, showfliers=False)
                axes[true_class, pred_class].set_ylim(0, 1)
                
                # 设置标题和标签
                if true_class == n_classes - 1:
                    axes[true_class, pred_class].set_xlabel(f'Pred {class_names[pred_class]}')
                if pred_class == 0:
                    axes[true_class, pred_class].set_ylabel(f'True {class_names[true_class]}')
            else:
                axes[true_class, pred_class].text(0.5, 0.5, 'No data', 
                                                 horizontalalignment='center',
                                                 verticalalignment='center',
                                                 transform=axes[true_class, pred_class].transAxes)
                axes[true_class, pred_class].set_ylim(0, 1)
    
    plt.suptitle('Prediction Probability Heatmap\n(True Class vs Predicted Class Probability)')
    plt.tight_layout()
    
    # 保存图像
    heatmap_path = os.path.join(save_dir, f"{model_name}_probability_heatmap.png")
    plt.savefig(heatmap_path)
    plt.close()
    
    return heatmap_path

# 绘制预测概率分布
def plot_prediction_distribution(y_true, y_prob, class_names, save_dir, model_name):
    """绘制每个类别的预测概率分布"""
    n_classes = len(class_names)
    fig, axes = plt.subplots(2, n_classes, figsize=(6*n_classes, 10))
    
    colors = ['red', 'green', 'blue', 'orange', 'purple'][:n_classes]
    
    # 为每个类别创建概率分布图
    for i, class_name in enumerate(class_names):
        # 获取属于当前类别的样本的概率
        class_probs = y_prob[y_true == i, i]
        
        # 绘制直方图
        axes[0, i].hist(class_probs, bins=30, alpha=0.7, color=colors[i])
        axes[0, i].set_title(f'Class {i} ({class_name})\nPrediction Probability Distribution')
        axes[0, i].set_xlabel('Predicted Probability')
        axes[0, i].set_ylabel('Frequency')
        axes[0, i].set_xlim(0, 1)
        
        # 绘制密度图
        sns.kdeplot(class_probs, ax=axes[1, i], color=colors[i], fill=True)
        axes[1, i].set_title(f'Class {i} ({class_name})\nProbability Density')
        axes[1, i].set_xlabel('Predicted Probability')
        axes[1, i].set_ylabel('Density')
        axes[1, i].set_xlim(0, 1)
    
    plt.tight_layout()
    
    # 保存图像
    dist_path = os.path.join(save_dir, f"{model_name}_prediction_distribution.png")
    plt.savefig(dist_path)
    plt.close()
    
    return dist_path

# 预测管道类 - 用于后续部署
class PredictionPipeline:
    def __init__(self, model_path, feature_groups, num_features, num_classes, model_params):
        # 初始化模型
        self.model = TimeSeriesTransformer(
            num_features=num_features,
            num_classes=num_classes,
            **model_params
        ).to(device)
        
        # 加载模型权重
        self.model.load_state_dict(torch.load(model_path))
        self.model.eval()
        
        # 存储特征分组信息
        self.feature_groups = feature_groups
        
    def prepare_input(self, raw_data_window):
        """使用与训练时相同的标准化逻辑准备输入"""
        return instance_normalization(raw_data_window, self.feature_groups)
    
    def predict(self, raw_data_window):
        # 准备输入
        input_data = self.prepare_input(raw_data_window)
        input_tensor = torch.tensor(input_data, dtype=torch.float32).unsqueeze(0)  # 添加batch维度
        input_tensor = input_tensor.to(device)
        
        # 模型预测
        with torch.no_grad():
            output = self.model(input_tensor)
            probabilities = torch.softmax(output, dim=1)
            prediction = torch.argmax(output, dim=1)
        
        return prediction.item(), probabilities.cpu().numpy()

# Optuna目标函数
def objective(trial):
    # 设置随机种子
    set_seed()
    
    # 在objective函数内部获取logger
    logger = logging.getLogger(__name__)
    
    # 定义超参数搜索空间
    hp = Hyperparameters()
    hp.d_model = trial.suggest_categorical('d_model', [32, 64, 128, 256])
    hp.nhead = trial.suggest_categorical('nhead', [4, 8, 16])
    hp.num_layers = trial.suggest_int('num_layers', 3, 6)
    hp.dim_feedforward = trial.suggest_categorical('dim_feedforward', [128, 256, 512, 1024])
    hp.dropout = trial.suggest_float('dropout', 0.3, 0.7)
    hp.learning_rate = trial.suggest_float('learning_rate', 1e-3, 1e-1, log=True)
    hp.window_size = trial.suggest_int('window_size', 50, 120, step=10)
    hp.optimizer_type = trial.suggest_categorical('optimizer_type', ['adam', 'sgd', 'adamw'])
    hp.weight_decay = trial.suggest_float('weight_decay', 1e-6, 1e-2, log=True)
    
    # 准备单只股票数据进行超参数优化
    data_dir = r"E:\stock\backtest\data\analyzed\5min"
    csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    
    if not csv_files:
        return 0.0
    
    # 选择一个文件进行超参数优化
    selected_file = random.choice(csv_files)
    file_path = os.path.join(data_dir, selected_file)
    
    # 如果是第一个trial，则输出标准化调试信息
    debug_output_path = None
    if trial.number == 0:
        debug_output_path = "normalization_debug.txt"
    train_loader, val_loader, class_weights, num_features, num_classes, _ = prepare_single_stock_data(file_path, hp, debug_output_path="normalization_debug.txt")
    
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
    
    # 训练模型（带早期淘汰）
    model, history, rejected = train_model_with_early_rejection(
        model, train_loader, val_loader, hp, class_weights, logger
    )
    
    # 如果被淘汰，返回一个较低的值
    if rejected:
        # 记录淘汰原因
        trial.set_user_attr('rejection_reason', 'poor_learning_curve')
        return 0.0
    
    # 评估模型
    val_loss, val_acc, val_f1, _, _, _ = evaluate_model_with_probs(model, val_loader)
    
    # 记录评估指标
    trial.set_user_attr('val_loss', val_loss)
    trial.set_user_attr('val_acc', val_acc)
    trial.set_user_attr('val_f1', val_f1)
    trial.set_user_attr('trial_params', str(hp.__dict__))
    
    # 记录当前试验信息
    logger.info(f"Trial {trial.number} completed with value: {val_acc:.4f}")
    logger.info(f"Trial params: {trial.params}")
    
    return val_acc

# 主函数
def main():
    # 解析命令行参数
    args = parse_args()
    
    # 设置日志记录
    logger = setup_logging()
    
    # 设置随机种子
    set_seed()
    
    # 获取所有CSV文件
    data_dir = args.data_dir
    csv_files = [os.path.join(data_dir, f) for f in os.listdir(data_dir) if f.endswith('.csv')]
    
    if not csv_files:
        logger.error("No CSV files found in directory")
        return
    
    # 超参数优化
    if not args.skip_optuna:
        logger.info("Starting hyperparameter optimization with Optuna...")
        study = optuna.create_study(direction='maximize')
        study.optimize(objective, n_trials=args.trials)
        
        logger.info("Best hyperparameters:")
        logger.info(study.best_params)
        logger.info(f"Best validation accuracy: {study.best_value:.4f}")
        
        # 保存所有试验结果
        trials_df = save_trial_results(study, "optuna_trials.csv")
        logger.info(f"Saved {len(trials_df)} trial results to optuna_trials.csv")
        
        # 打印前10个最佳试验
        print_top_trials(study, n=10, logger=logger)
        
        # 使用最佳超参数训练最终模型
        logger.info("Training final model with best hyperparameters...")
        hp = Hyperparameters()
        
        # 更新超参数
        best_params = study.best_params
        for key, value in best_params.items():
            setattr(hp, key, value)
    else:
        # 跳过超参数优化，使用预定义的最佳参数
        logger.info("Skipping hyperparameter optimization, using pre-defined best parameters...")
        hp = Hyperparameters()
        
        # 使用预定义的最佳参数
        best_params = {
            'd_model': 64, 'nhead': 8, 'num_layers': 3, 'dim_feedforward': 256, 
            'dropout': 0.1, 'learning_rate': 0.001, 'window_size': 50, 
            'optimizer_type': 'adam', 'weight_decay': 1e-5
        }
        
        for key, value in best_params.items():
            if hasattr(hp, key):
                setattr(hp, key, value)
            else:
                logger.warning(f"Parameter {key} not found in Hyperparameters class")
    
    # 准备多股票数据
    train_loader, test_loader, class_weights, num_features, num_classes = prepare_multi_stock_data(csv_files, hp)
    
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
    model, history, rejected = train_model_with_early_rejection(
        model, train_loader, test_loader, hp, class_weights, logger
    )
    
    # 评估模型并获取概率
    test_loss, test_acc, test_f1, predictions, targets, probabilities = evaluate_model_with_probs(model, test_loader)
    logger.info(f"Test results - Loss: {test_loss:.4f}, Accuracy: {test_acc:.4f}, F1: {test_f1:.4f}")
    
    # 创建保存目录
    os.makedirs(args.save_dir, exist_ok=True)
    
    # 生成模型名称
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_name = f"model_{timestamp}_acc{test_acc:.4f}"
    
    # 保存模型
    model_path = save_model(model, args.save_dir, model_name)
    logger.info(f"Model saved to: {model_path}")
    
    # 保存模型配置（用于后续预测）
    model_config = {
        'num_features': num_features,
        'num_classes': num_classes,
        'model_params': {
            'd_model': hp.d_model,
            'nhead': hp.nhead,
            'num_layers': hp.num_layers,
            'dim_feedforward': hp.dim_feedforward,
            'dropout': hp.dropout,
            'use_cls_token': hp.use_cls_token,
            'use_time_encoding': hp.use_time_encoding,
            'use_position_encoding': hp.use_position_encoding
        },
        'feature_groups': hp.feature_groups,
        'window_size': hp.window_size
    }
    
    config_path = os.path.join(args.save_dir, f"{model_name}_config.json")
    with open(config_path, 'w') as f:
        json.dump(model_config, f, indent=4)
    logger.info(f"Model config saved to: {config_path}")
    
    # 绘制并保存可视化图表
    class_names = [f'Class {i}' for i in range(num_classes)]
    
    # ROC AUC曲线
    roc_auc, roc_path = plot_roc_auc(targets, np.array(probabilities), class_names, args.save_dir, model_name)
    logger.info(f"ROC AUC saved to: {roc_path}")
    for i, auc_value in enumerate(roc_auc):
        if i < len(class_names):
            logger.info(f"Class {i} AUC: {auc_value:.4f}")
    
    # 概率热力图
    heatmap_path = plot_probability_heatmap(
        np.array(targets), np.array(predictions), np.array(probabilities), 
        class_names, args.save_dir, model_name
    )
    logger.info(f"Probability heatmap saved to: {heatmap_path}")
    
    # 预测概率分布图
    dist_path = plot_prediction_distribution(
        np.array(targets), np.array(probabilities), class_names, args.save_dir, model_name
    )
    logger.info(f"Prediction distribution saved to: {dist_path}")
    
    # 输出详细分类报告
    logger.info("\nClassification report:")
    logger.info(classification_report(targets, predictions, target_names=class_names))
    
    logger.info("Confusion matrix:")
    logger.info(confusion_matrix(targets, predictions))
    
    # 释放GPU内存
    del model
    torch.cuda.empty_cache()
    
    return test_acc, test_f1, history, model_path

if __name__ == "__main__":
    test_acc, test_f1, history, model_path = main()
    print(f"Final test accuracy: {test_acc:.4f}")
    print(f"Final test F1 score: {test_f1:.4f}")
    print(f"Model saved at: {model_path}")