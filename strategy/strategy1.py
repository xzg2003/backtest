from config import *
import pandas as pd
import numpy as np
import os
class strategy():
    def __init__(self, x_pre_test, param):
        if os.path.exists('./data/pre.csv'):
            self.x_pre_test = pd.read_csv('./data/pre.csv')
        else:
            self.x_pre_test = x_pre_test
        
        self.t = param['t']

    def run(self):
        self.result = []
        for instrument in instruments:
            df = self.x_pre_test[self.x_pre_test['instrument'] == instrument].copy()
            df['pos'] = np.where(df['pre'] > self.t, 1, np.where(df['pre'] < -self.t, -1 ,0))
            self.result.append(df)
        
        self.result = pd.concat(self.result, axis=0, ignore_index=True)
        self.result.to_csv('./data/position.csv',index=False)