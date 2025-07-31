"""
回测模块

该模块包含量化交易策略的回测功能，主要包括订单生成和绩效评估两个核心组件。
提供完整的回测流程，从信号生成到订单执行再到绩效分析。

主要功能包括：
1. 根据模型预测结果生成交易订单
2. 计算和分析策略的各项绩效指标
3. 提供完整的回测流程支持

子模块：
- gen_orders: 交易订单生成模块
- performance4: 回测绩效评估模块
"""

# 导入回测模块的主要组件
from .gen_orders import Trade_Orders
from .performance4 import *

__all__ = [
    'Trade_Orders',
    'performance4'
]