
import time
import random
import os
import sys
sys.path.append(os.getcwd())

from dotenv import dotenv_values
#env_vars = dotenv_values("/data/Finance/Factor/factor/.env")
#file_store_path = env_vars['file_store_path']

# 为对接CTP 处理的ID和tradeId
def generate_unique_string():
    # 获取当前时间戳
    timestamp = int(time.time() * 1000)
    
    # 生成4位随机数
    random_str = ''.join(str(random.randint(0, 9)) for _ in range(6))
    
    # 拼接时间戳和随机数
    result = str(timestamp) + random_str
    
    # 截取前12个字符作为最终结果
    result = result[-12:]
    
    return result
