def get_money_flow_step(*args, **kwargs):
    return {}

#!/usr/bin/env python
# coding: utf-8

# In[2]:


# 获取平安银行, 贵州茅台2023年2月1日前3天的特大单买入数据
from core.base_strategy import BaseStrategy
value = get_money_flow_step(
    security_list=['300765.SZ'],
    start_date=None,
    end_date='20251204',
    fre_step='1d',
    fields=['act_buy_xl', 'pas_buy_xl', 
                'act_buy_l', 'pas_buy_l',
                'act_buy_m', 'pas_buy_m', 
                'act_sell_xl', 'pas_sell_xl', 
                'act_sell_l', 'pas_sell_l',
                'act_sell_m', 'pas_sell_m',
                'buy_l', 'sell_l',
                'dde_l', 'net_flow_rate','l_net_value'],
    count=1,
    is_panel=0
)
# 打印主动买入特大单金额数据
print(value) 

# In[ ]:






class UntitledStrategy(BaseStrategy):
    """基于Untitled的策略"""
    
    def __init__(self, data, params=None):
        super().__init__(data, params)
        # 初始化代码
        self.name = "UntitledStrategy"
        self.description = "基于Untitled的策略"
        
    def calculate_signals(self, df):
        """计算交易信号"""
        # 策略逻辑
        return df
        
    def generate_signals(self, df):
        """生成交易信号"""
        # 信号生成逻辑
        return df
