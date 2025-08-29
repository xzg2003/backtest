# FCT_Tsi_Atr_Dfive：趋势强度与ATR归一化因子，衡量单位波动下的趋势强度

import os

import numpy
import pandas

from config import k_line_type

# 设置工作目录为当前脚本所在的目录
os.chdir(os.path.dirname(os.path.abspath(__file__)))


class FCT_Tsi_Atr_Dfive:
    def __init__(self):
        self.factor_name = 'FCT_Tsi_Atr_Dfive'

    def formula(self, param):
        # 从参数字典中提取 DataFrame
        df = param.get('df', None)
        if df is None:
            raise ValueError("no 'df' in param")

        # 从参数字典中提取length
        length = param.get('length', None)

        # 从参数字典中提取 atr_length
        atr_length = param.get('atr_length', None)
        if atr_length is None:
            raise ValueError("no 'atr_length' in param")

        # 从参数字典中提取 factor_name
        factor_name = param.get('factor_name', None)
        if factor_name is None:
            raise ValueError("no 'factor_name' in param")

        # 从参数字典中获取 instrument
        instrument = param.get('instrument', None)
        if instrument is None:
            raise ValueError("param miss instrument")

        # 初始化 new_columns 用于统一管理中间变量
        new_columns = pandas.DataFrame(index=df.index)

        # 导入先前Tsi的计算结果
        tsi_series = param.get(f'FCT_Tsi_1@{length}', None)
        if tsi_series is None:
            tsi_data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                         f'../data/{k_line_type}/{instrument}/FCT_Tsi_1@{length}.csv')

            tsi_df = pandas.read_csv(tsi_data_path)
            if 'datetime' in df.columns and 'datetime' in tsi_df.columns:
                tsi_series = pandas.merge(df[['datetime']], tsi_df, on='datetime', how='left')[f'FCT_Tsi_1@{length}']
            else:
                tsi_series = tsi_df[f'FCT_Tsi_1@{length}']

        new_columns['TSI'] = tsi_series.reset_index(drop=True)

        # 计算 ATR
        high_low = df['high'] - df['low']
        high_close = numpy.abs(df['high'] - df['close'].shift(1))
        low_close = numpy.abs(df['low'] - df['close'].shift(1))
        tr = pandas.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        new_columns['ATR'] = tr.rolling(window=atr_length).mean()

        # 归一化：TSI / ATR
        new_columns[f'{factor_name}'] = new_columns['TSI'] / (new_columns['ATR'] + 1e-10)

        # 合并到主表
        df = pandas.concat([df, new_columns], axis=1)

        # 返回结果（无日期）
        result = df[[f'{factor_name}']].copy()
        return result
