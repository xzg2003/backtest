
# vol排序前10 涨跌幅相加

'''
vol_value:= vol;
return:=(close-ref(close,1))/ref(close,1);
INPUT:N(20,20,1000,1); // 20 40

V1:=LARGE(vol_value,N,1);
V2:=LARGE(vol_value,N,2);
V3:=LARGE(vol_value,N,3);
V4:=LARGE(vol_value,N,4);
V5:=LARGE(vol_value,N,5);
V6:=LARGE(vol_value,N,6);
V7:=LARGE(vol_value,N,7);
V8:=LARGE(vol_value,N,8);
V9:=LARGE(vol_value,N,9);
V10:=LARGE(vol_value,N,10);

C1:=REF(return,barslast(vol_value=v1));
C2:=REF(return,barslast(vol_value=v2));
C3:=REF(return,barslast(vol_value=v3));
C4:=REF(return,barslast(vol_value=v4));
C5:=REF(return,barslast(vol_value=v5));
C6:=REF(return,barslast(vol_value=v6));
C7:=REF(return,barslast(vol_value=v7));
C8:=REF(return,barslast(vol_value=v8));
C9:=REF(return,barslast(vol_value=v9));
C10:=REF(return,barslast(vol_value=v10));

signal:(C1+C2+C3+C4+C5+C6+C7+C8+C9+C10)*100;
波动率:= ma(TR,200)*100/open;
OUT:signal/波动率;



'''
import numpy as np
import pandas as pd

from .constants import MIN_MAX
from .factor_template import FactorTemplate

class  FCT_Avg_Amt_Big_Count_1(FactorTemplate):

    def __init__(self):
        super().__init__()
        self.factor_name = 'FCT_Avg_Amt_Big_Count_1'

    
    def formula(self,**param):
        df = param['df'].copy()
        Length = param['Length']
        Count = param['Count']
        TrLength = param['TRLength']
        if(Count==pd.NaT or Count==0 or Length<=Count):
            return

        # 计算tr
        df['Close_prev'] = df['close'].shift(1)
        df['tr'] = df[['high', 'low', 'Close_prev']].apply(lambda x: max(x[0] - x[1], abs(x[0] - x[2]), abs(x[1] - x[2])), axis=1)
        # 计算出每根K线的return
        df['return'] = (df['close'] - df['close'].shift(1)) / df['close'].shift(1)
        
        df['signal'] = 0
        # 循环数据，对每行往前取Length周期内的df进行排序
        # 排序前10的行即为要取return值计算行
        for index, row in df.iterrows():
            # 数据不满Length则跳过
            if index<Length:
                continue
            # 包含当前行，截取Length个周期数据作为新df，并且重置原有index
            df_temp = df[index-Length+1:index+1].reset_index(drop=True)
            # 对以上df按成交量进行降序排序
            df_sorted = df_temp.sort_values('volume', ascending=False)

            #V1-V10  这里仅做验证，后续计算不需要用到
            #v = df_sorted['volume']

            #C1-C10 排序过后的df前10行return值即为要获取的C1-C10数据
            c = df_sorted[:Count]['return']

            #计算signal：对C1-C10求和乘100
            df.at[index,'signal']= c.sum()*100

            
        df['wave_rate'] = df['tr'].rolling(window=TrLength).mean() * 100 / df['open']

        # 计算out
        df['output'] =np.where(df['wave_rate']==0,0, df['signal'] / df['wave_rate'])
        
        if MIN_MAX[self.factor_name] !=None and (Length in MIN_MAX[self.factor_name]):
            min_max = MIN_MAX[self.factor_name][Length]
            df['output'] = np.where(df['output']>min_max['max'],min_max['max'],
                                    np.where(df['output']<min_max['min'],min_max['min'],df['output']))
        # TODO 下面的保存需要删除
        if param['save'] is not None:
            df.to_csv(param['save'], index=False)
        return df['output']