import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler, StandardScaler
import joblib


class DataPreprocessor:
    def __init__(self, lookback=60, feature_columns=['close']):
        self.lookback = lookback
        self.feature_columns = feature_columns
        self.scaler = StandardScaler()  # ✅ 显式初始化 scaler

    def save(self, path):
        joblib.dump(self, path)

    @classmethod
    def load(cls, path):
        return joblib.load(path)

    
    def preprocess(self, data, test_size=0.2, return_test=True):
        data = self._generate_labels(data)
        
        # 1. 分割数据集
        split_idx = int(len(data) * (1 - test_size))
        train_data = data.iloc[:split_idx]
        test_data = data.iloc[split_idx:]
        
        # 2. 仅用训练集拟合归一化
        scaled_train = np.column_stack([
            self.scalers[col].fit_transform(train_data[[col]].values)
            for col in self.feature_columns
        ])
        scaled_test = np.column_stack([
            self.scalers[col].transform(test_data[[col]].values)
            for col in self.feature_columns
        ])
        
        # 生成数据
        X_train, y_dir_train, y_amp_train = self.create_sequences(scaled_train, train_data)
        X_test, y_dir_test, y_amp_test = self.create_sequences(scaled_test, test_data)
        
        if return_test:
            # 返回训练集和测试集
            return X_train, y_dir_train, y_amp_train, X_test, y_dir_test, y_amp_test
        else:
            # 仅返回训练集
            return X_train, y_dir_train, y_amp_train
    # 3. 生成序列（简化版）
    def create_sequences(self, scaled_data, raw_data):
        """确保每个预测点对应正确的未来价格"""
        X, y_dir, y_amp = [], [], []
        for i in range(self.lookback, len(scaled_data)):
            # 输入窗口: [t-lookback, t-1]
            X.append(scaled_data[i - self.lookback:i])
            # 输出标签: t 时刻的涨跌幅和方向
            y_dir.append(raw_data.iloc[i]["direction"])
            y_amp.append(raw_data.iloc[i]["amplitude"])
        return np.array(X), np.array(y_dir), np.array(y_amp)
    def prepare_new_data(self, new_data):
        """新数据预处理"""
        scaled = np.column_stack([
            self.scalers[col].transform(new_data[[col]].values)
            for col in self.feature_columns
        ])
        return scaled[-self.lookback:].reshape(1, self.lookback, -1)
    def fit_transform(self, data):
        """训练阶段：生成标签、清洗数据并拟合参数"""
        # 生成标签
        data = self._generate_labels(data)
        
        # ✅ 直接在此处清洗数据（无需 _clean_data 方法）
        data = data.dropna(subset=['amplitude'])
        data = data[np.isfinite(data['amplitude'])]
        
        # 拟合参数并转换数据
        self.fit(data)
        scaled_data = self.scaler.transform(data[self.feature_columns])
        return scaled_data

    def fit(self, data):
        # 使用 DataFrame 的列名进行拟合
        self.scaler.fit(data[self.feature_columns])
        return self

    def transform(self, data):
        # 使用 DataFrame 的列名进行转换
        scaled = self.scaler.transform(data[self.feature_columns])
        return scaled

    def _generate_labels(self, data):
        """生成标签（仅在训练时调用）"""
        data = data.copy()
        data['amplitude'] = data['close'].pct_change().shift(-1)  # 预测未来涨跌幅
        data['direction'] = np.where(data['amplitude'] > 0, 1, 0).astype(np.float32)
        return data

    def _scale_features(self, data):
        """标准化特征（不涉及标签）"""
        return self.scaler.transform(data[self.feature_columns])