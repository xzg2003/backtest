#from backtesting.config import *
from config import DATA_DIR, k_line_type
import os
import pandas as pd
mindiff = pd.read_csv('mindiff.csv')
mul = pd.read_csv('future_mul.csv')

def prepare_data(year, instruments, factor_list, target, k_line_type):
    # 遍历所有的期货种类
    st = f'{year}-01-01'
    et = f'{year}-12-31'
    df_pre = []
    df_train = []
    df_pre_pre = []
    for instrument in instruments:
        # 构建数据路径data_path
        data_path = f'{DATA_DIR}/{k_line_type}/{instrument}'
        if os.path.exists(f'{data_path}/{instrument}.csv'):
            df = pd.read_csv(f'{data_path}/{instrument}.csv')
            df['mindiff'] = mindiff[mindiff['instrument'] == instrument]['mindiff'].item()
            df['mul'] = mindiff[mindiff['instrument'] == instrument]['mul'].item()            
            #print(df)
            if 'underlying_symbol' in df.columns:
                df.rename(columns={'underlying_symbol': 'instrument'}, inplace=True)
            if 'date' in df.columns:
                df.rename(columns={'date': 'datetime'}, inplace=True)
                df['trading_date'] = df['datetime']
            if 'dominant_id' in df.columns:
                df.rename(columns={'dominant_id': 'instrument_id'}, inplace=True)

        df_pre_pre.append(df[(df['datetime'] >= st) & (df['datetime'] <= et)])
        if len(factor_list)==0:
            pass
        else:
            for factor in factor_list:
                df[factor] = pd.read_csv(f'{data_path}/{factor}.csv')[factor]
            df[target] = pd.read_csv(f'{data_path}/{target}.csv')[target]
        
        df_pre.append(df[(df['datetime'] >= st) & (df['datetime'] <= et)])
        df_train.append(df[(df['datetime'] < st)])
    
    df_train = pd.concat(df_train, axis=0)
    df_pre = pd.concat(df_pre, axis=0)
    df_pre_pre = pd.concat(df_pre_pre, axis=0)
    return df_train, df_pre, df_pre_pre