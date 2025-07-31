"""
回测通用模块
包含回测过程中使用的各种通用函数和工具方法
"""

import os
import random
import sys
import time

sys.path.append(os.getcwd())


# env_vars = dotenv_values("/data/Finance/Factor/factor/.env")
# file_store_path = env_vars['file_store_path']

def generate_unique_string():
    """
    生成唯一的字符串ID

    该函数用于为交易订单生成唯一标识符，模仿CTP接口的ID生成方式。
    通过组合时间戳和随机数生成一个唯一的12位字符串。

    Returns
    -------
    str
        12位唯一字符串，由时间戳和随机数组成
        格式示例: "162345678901"
    """
    # 获取当前时间戳
    timestamp = int(time.time() * 1000)

    # 生成4位随机数
    random_str = ''.join(str(random.randint(0, 9)) for _ in range(6))

    # 拼接时间戳和随机数
    result = str(timestamp) + random_str

    # 截取前12个字符作为最终结果
    result = result[-12:]

    return result
