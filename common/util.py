

# 创建文件夹
import os
import pickle
import datetime
import time

from dotenv import dotenv_values
import pandas as pd

#env_vars = dotenv_values("/data/Finance/Factor/factor/.env")
# print(env_vars)

# 因子配置文件路径
#config_yaml_path = env_vars['config_yaml_path']
#file_store_path = env_vars['file_store_path']
config_yaml_path='config.yaml'
file_store_path='.'

def mkdir(path):
    if not os.path.exists(path):
        os.makedirs(path)

# 保存文件(不压缩)
def save_file(data, save_file_path):
    f = open(save_file_path, 'wb')
    pickle.dump(data, f)

# 读取文件(不压缩)
def load_file(file_path):
    try:
        pickle_file = open(file_path, 'rb')
        df = pickle.load(pickle_file)
        return df
    except Exception as ex:
        print(f'error--{file_path}')
        print(ex)
        return pd.DataFrame()
    
# 删除文件
def delete_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
    else:
        print("文件不存在")
        
# 检查文件是否存在
def check_file_exists(file_path):
    if os.path.exists(file_path):
        return True
    else:
        return False

# 方法执行耗时计算
class Calc_Time():
    def __init__(self,txt="",level=0):
        self.level=level
        self.st = datetime.datetime.now()
        self.txt=f' ---- {txt} :: time spend'
    
    def t(self):
        #env_level= env_vars['log_level']
        #if env_vars!="0":
        #    if self.level < int(env_level):
        #        return
        et = datetime.datetime.now()
        diff = et -self.st
        print(f" {self.txt} -- {diff} ----")

