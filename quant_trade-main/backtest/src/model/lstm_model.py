from tensorflow.keras import backend as K
from tensorflow.keras.layers import Input, LSTM, Dense, Dropout, Concatenate, Bidirectional, Attention
from tensorflow.keras.models import Model
from tensorflow.keras.losses import Loss  # ✅ 继承Loss基类
from tensorflow.keras import saving
from tensorflow.keras.losses import MeanSquaredError
from tensorflow import keras
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.layers import GlobalAveragePooling1D, RepeatVector
from keras.regularizers import l2
from keras.layers import Lambda
from keras.losses import BinaryCrossentropy, MeanSquaredError
from keras.metrics import BinaryAccuracy, MeanAbsoluteError
class DynamicLossWeights(Loss):
    def __init__(self, alpha=0.6, name="dynamic_loss"):
        super().__init__(name=name)
        self.alpha = alpha

    def get_config(self):
        return {"alpha": self.alpha}  # ✅ 支持模型保存/加载

    def call(self, y_true, y_pred):
        dir_true, amp_true = y_true[0], y_true[1]
        dir_pred, amp_pred = y_pred[0], y_pred[1]
        
        dir_loss = K.binary_crossentropy(dir_true, dir_pred)
        amp_loss = K.mean(K.square(amp_true - amp_pred))
        
        dir_acc = K.mean(K.cast(K.equal(dir_true, K.round(dir_pred)), 'float32'))
        alpha = K.switch(dir_acc < 0.6, self.alpha + 0.2, self.alpha)
        return alpha * dir_loss + (1 - alpha) * amp_loss


@keras.saving.register_keras_serializable()
def custom_mse(y_true, y_pred):
    epsilon = 1e-7  # 防止除零或对数溢出
    y_true = keras.backend.clip(y_true, epsilon, None)  # 确保标签 >0
    y_pred = keras.backend.clip(y_pred, epsilon, None)
    return MeanSquaredError()(y_true, y_pred)

def build_lstm_model(lookback, num_features=1):
    inputs = Input(shape=(lookback, num_features))
    
    # ------------------- 方向分支 -------------------
    x_dir = LSTM(64, 
                return_sequences=True,
                dropout=0.2,
                recurrent_dropout=0.1,
                kernel_regularizer=l2(1e-4)
               )(inputs)
    
    x_dir = LSTM(32, 
                return_sequences=True,
                dropout=0.2,
                recurrent_dropout=0.1,
                kernel_regularizer=l2(1e-4)
               )(x_dir)
    
    # 注意力层
    x_dir = Attention()([x_dir, x_dir, x_dir])
    x_dir = Dropout(0.3)(x_dir)
    
    # ------------------- 幅度分支 -------------------
    x_amp = LSTM(128, 
                 return_sequences=True,
                 dropout=0.2,
                 recurrent_dropout=0.1,
                 kernel_regularizer=l2(1e-4)
                )(inputs)
    
    x_amp = LSTM(64, 
                 return_sequences=True,
                 dropout=0.2,
                 recurrent_dropout=0.1,
                 kernel_regularizer=l2(1e-4)
                )(x_amp)
    
    x_amp = LSTM(32, 
                 return_sequences=True,
                 dropout=0.2,
                 recurrent_dropout=0.1,
                 kernel_regularizer=l2(1e-4)
                )(x_amp)
    
    # ------------------- 特征融合 -------------------
    attention = Attention()([x_amp, x_dir, x_dir])
    attention = Dropout(0.3)(attention)
    
    combined = Concatenate()([x_amp, attention])
    combined = Dense(64, 
                    activation='relu',
                    kernel_regularizer=l2(1e-4)
                   )(combined)
    combined = Dropout(0.3)(combined)
    
    # ------------------- 输出层关键修改 -------------------
    # 用 Lambda 层显式包装切片操作
    x_dir_last = Lambda(lambda x: x[:, -1, :], name='get_last_timestep_dir')(x_dir)
    combined_last = Lambda(lambda x: x[:, -1, :], name='get_last_timestep_combined')(combined)
    
    # 输出层
    direction = Dense(1, 
                     activation='sigmoid',
                     kernel_regularizer=l2(1e-4),
                     name='direction'
                    )(x_dir_last)  # ✅ 使用 Lambda 层输出
    
    amplitude = Dense(1, 
                     activation='linear',
                     kernel_regularizer=l2(1e-4),
                     name='amplitude'
                    )(combined_last)  # ✅ 使用 Lambda 层输出
    
    # ------------------- 编译模型 -------------------
    model = Model(inputs=inputs, outputs=[direction, amplitude])
    model.compile(
        optimizer=Adam(learning_rate=1e-4),
        loss={
            'direction': BinaryCrossentropy(),  # ✅ 使用函数对象
            'amplitude': MeanSquaredError()      # ✅ 使用函数对象
        },
        loss_weights=[0.6, 0.4],
        metrics={
            'direction': BinaryAccuracy(),      # ✅ 使用函数对象
            'amplitude': MeanAbsoluteError()    # ✅ 使用函数对象
        }
    )
    return model