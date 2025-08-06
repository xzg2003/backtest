import argparse
import joblib
import pandas as pd
from pymongo import UpdateOne
import xgboost as xgb1
import common.util as zutil

class model():
    def __init__(self, instruments, x_train, y_train, x_test, x_pre_test, param):
        self.x_train = x_train # 训练集的特征
        self.y_train = y_train # 训练集的标签
        self.x_test = x_test # 测试集的特征
        self.x_pre_test = x_pre_test # 存放市场数据与模型预测结果合并后的表格
        self.instruments = instruments
        self.Depth = param['max_depth']
        pass
    
    def start_train(self):

        # n_job = multiprocessing.cpu_count() * 8 // 10
        model=xgb1.XGBRegressor(
            max_depth=self.Depth,  # 深度 6 - 7 - 8 - 9
            base_score=0,
            learning_rate=0.1,  # 0.0001 - 0.1   10倍 提升
            # 设置较小的 eta 就可以多学习几个弱学习器来弥补不足的残差
            # 推荐 [0.01, 0.015, 0.025, 0.05, 0.1] 0.1 可减少迭代用时
            n_estimators=200,  # 树的棵数 150 -  200 #  50 - 150  50 提升
            objective='reg:linear',  # 此默认参数与 XGBClassifier 不同
            booster='gbtree',  # 推荐 gbtree
            # importance_type='gain',
            # n_jobs=n_job,
            # random_state=8).fit(data, y, sample_weight=weights)  # 使用权重
            random_state=8).fit(self.x_train, self.y_train) # 不使用权重
        joblib.dump(model, f'model_test.pkl')

    
    # 使用训练好的模型预测数据
    def use_model(self):
        try:
            model = joblib.load(f'model_test.pkl')
            predictions = model.predict(self.x_test)
            self.x_pre_test[f'pre_real'] = predictions.copy()
            t = zutil.Calc_Time("use model ")
            df_new = pd.DataFrame()
            for ins_id in self.instruments:
                df = self.x_pre_test[self.x_pre_test['instrument']==ins_id].copy()
                if len(df)==0:
                    continue
                df = df.sort_values(by='datetime', ascending=True)
                df.reset_index(drop=True,inplace=True)
                df["pre"] =df["pre_real"].shift(1)
                df_new = pd.concat([df_new,df])
            
            df_new.to_csv('./data/pre.csv',index=False)
            t.t()
        except Exception as ex:
            print(ex)
        pass

    def run(self):
        self.start_train()
        self.use_model()