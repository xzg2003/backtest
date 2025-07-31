"""
通用工具模块
提供文件操作、时间计算等通用工具函数
"""

import datetime
# 创建文件夹
import os
import pickle

import pandas as pd

# env_vars = dotenv_values("/data/Finance/Factor/factor/.env")
# print(env_vars)

# 因子配置文件路径
# config_yaml_path = env_vars['config_yaml_path']
# file_store_path = env_vars['file_store_path']
config_yaml_path = 'config.yaml'
file_store_path = '.'


def mkdir(path):
    """
    创建文件夹

    Parameters
    ----------
    path : str
        要创建的文件夹路径
    """
    if not os.path.exists(path):
        os.makedirs(path)


def save_file(data, save_file_path):
    """
    保存数据到文件(使用pickle序列化，不压缩)

    Parameters
    ----------
    data : object
        要保存的数据
    save_file_path : str
        保存文件的路径
    """
    f = open(save_file_path, 'wb')
    pickle.dump(data, f)


def load_file(file_path):
    """
    从文件加载数据(使用pickle反序列化，不压缩)

    Parameters
    ----------
    file_path : str
        要加载的文件路径

    Returns
    -------
    object
        加载的数据，如果加载失败则返回空的DataFrame
    """
    try:
        pickle_file = open(file_path, 'rb')
        df = pickle.load(pickle_file)
        return df
    except Exception as ex:
        print(f'error--{file_path}')
        print(ex)
        return pd.DataFrame()


def delete_file(file_path):
    """
    删除文件

    Parameters
    ----------
    file_path : str
        要删除的文件路径
    """
    if os.path.exists(file_path):
        os.remove(file_path)
    else:
        print("文件不存在")


def check_file_exists(file_path):
    """
    检查文件是否存在

    Parameters
    ----------
    file_path : str
        要检查的文件路径

    Returns
    -------
    bool
        文件存在返回True，否则返回False
    """
    if os.path.exists(file_path):
        return True
    else:
        return False


class Calc_Time():
    """
    时间计算类
    用于计算方法执行耗时

    Attributes
    ----------
    level : int
        日志级别
    st : datetime.datetime
        开始时间
    txt : str
        描述文本
    """

    def __init__(self, txt="", level=0):
        """
        初始化时间计算实例

        Parameters
        ----------
        txt : str, optional
            描述文本，默认为空字符串
        level : int, optional
            日志级别，默认为0
        """
        self.level = level
        self.st = datetime.datetime.now()
        self.txt = f' ---- {txt} :: time spend'

    def t(self):
        """
        输出时间消耗
        计算并打印从初始化到调用此方法的时间差
        """
        # env_level= env_vars['log_level']
        # if env_vars!="0":
        #    if self.level < int(env_level):
        #        return
        et = datetime.datetime.now()
        diff = et - self.st
        print(f" {self.txt} -- {diff} ----")
