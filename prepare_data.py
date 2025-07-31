"""
数据准备模块
负责加载和处理用于模型徐连和回测的期货数据
"""

import os

import pandas as pd

# from backtesting.config import *
from config import DATA_DIR

# 加载最小变动单位和合约乘数数据
mindiff = pd.read_csv('mindiff.csv')
mul = pd.read_csv('future_mul.csv')


def prepare_data(year, instruments, factor_list, target, k_line_type):
    """
    准备训练和预测所需的数据

    该函数根据指定年份和期货品种列表，加载历史数据、因子数据和目标变量，
    并将数据划分为训练集和预测集

    Parameters
    ----------
    year : int
        数据年份
    instruments : list
        期货品种列表
    factor_list : list
        因子列表
    target : str
        目标变量名称
    k_line_type : str
        K线类型

    Returns
    -------
    tuple
        包含三个元素的元组:
        - df_train (pandas.DataFrame): 训练数据集，包含指定年份之前的所有数据
        - df_pre (pandas.DataFrame): 预测数据集，包含指定年份的数据及因子
        - df_pre_pre (pandas.DataFrame): 基础预测数据集，仅包含指定年份的原始数据
    """
    # 设置数据时间范围
    st = f'{year}-01-01'  # 开始时间
    et = f'{year}-12-31'  # 结束时间

    # 初始化数据列表
    df_pre = []  # 预测数据
    df_train = []  # 训练数据
    df_pre_pre = []  # 基础预测数据（不包含因子）

    # 遍历所有的期货品种
    for instrument in instruments:
        # 构建数据路径data_path
        data_path = f'{DATA_DIR}/{k_line_type}/{instrument}'

        # 检查主数据文件是否存在
        if os.path.exists(f'{data_path}/{instrument}.csv'):
            # 读取主数据文件
            df = pd.read_csv(f'{data_path}/{instrument}.csv')

            # 添加最小变动价位和合约乘数信息
            df['mindiff'] = mindiff[mindiff['instrument'] == instrument]['mindiff'].item()
            df['mul'] = mindiff[mindiff['instrument'] == instrument]['mul'].item()

            # 数据列名标准化处理
            if 'underlying_symbol' in df.columns:
                # 重命名underlying_symbol列为instrument
                df.rename(columns={'underlying_symbol': 'instrument'}, inplace=True)
            if 'date' in df.columns:
                # 重命名date列为datetime，并添加trading_date列
                df.rename(columns={'date': 'datetime'}, inplace=True)
                df['trading_date'] = df['datetime']
            if 'dominant_id' in df.columns:
                # 重命名dominant_id列为instrument_id
                df.rename(columns={'dominant_id': 'instrument_id'}, inplace=True)

        # 将指定年份的基础数据添加到df_pre_pre列表
        df_pre_pre.append(df[(df['datetime'] >= st) & (df['datetime'] <= et)])

        # 如果因子列表不为空，则加载因子数据
        if len(factor_list) == 0:
            # 因子列表为空时不进行任何操作
            pass
        else:
            # 遍历因子列表，加载每个因子的数据
            for factor in factor_list:
                df[factor] = pd.read_csv(f'{data_path}/{factor}.csv')[factor]
            # 加载目标变量数据
            df[target] = pd.read_csv(f'{data_path}/{target}.csv')[target]

        # 将指定年份的完整数据（包含因子）添加到df_pre列表
        df_pre.append(df[(df['datetime'] >= st) & (df['datetime'] <= et)])
        # 将指定年份之前的数据添加到训练数据列表
        df_train.append(df[(df['datetime'] < st)])

    # 合并所有训练数据
    df_train = pd.concat(df_train, axis=0)
    # 合并所有预测数据
    df_pre = pd.concat(df_pre, axis=0)
    # 合并所有基础预测数据
    df_pre_pre = pd.concat(df_pre_pre, axis=0)

    # 返回训练数据、预测数据和基础预测数据
    return df_train, df_pre, df_pre_pre
