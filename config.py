global train_list

DATA_DIR = 'C:/wzx\KCL/dataset/future_data' # 数据目录
k_line_type = '1d' # K线类型

model_name ='xgb' # 模型名称
model_param = {'max_depth': 6} # 模型参数

# 输入参与回测的因子，为空则所有因子全部参与
train_list=['FCT_Ar_1@5','FCT_Ac_Tr_1@5','FCT_Cmf_1@5','FCT_Br_1@5']
# 需要预测的指标
target_list = ['FCT_CHG@1']
enter_count = 0
# 需要进行回测的年份，用该年份以前的数据进行训练，该年份进行预测
years_list=[2022,2023]
# 手续费率
FEE_FEE=0.0002
# 启动资金
AMOUNT_4_OPEN = 1000000

instruments= ['A','AG']#,'AL','AP','AU','BU','C','CF','CJ','CS',
             #'CU','EB','EG','FG','FU','HC','I','IC','IF','IH',
            #'J','JD','JM','L','LU','LH','M','MA','NI','OI','P',
            #'PB','PF','PG','PK','PP','RB','RM','RU','SA','SF',
            #'SM','SN','SP','SR','SC','SS','TA','T','TF','UR','V','Y','ZN'] #期货类型