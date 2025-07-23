# 回测流程里面的公共方法
import pandas as pd

# 拷贝一份base_factors 到factors
# 然后删除factors 里面包含enter的行
# get_group_df 直接读取删除后的数据
def delete_enter_4_base(base_dir):
    base_factors_df = pd.read_csv(f'{base_dir}/base_factors.csv')
    enter_df = pd.read_csv(f'{base_dir}/enter.csv')
    df_c = pd.merge(enter_df, base_factors_df, on='feature', how='outer', indicator=True)
    df_c = df_c[df_c['_merge'] == 'right_only']
    df_c = df_c.drop('_merge', axis=1)
    df_c.to_csv(f'{base_dir}/factors.csv',index=False)

def get_group_df(base_dir,tyeps="group"):
    '''
    base_dir : 基础路径
    types : all/group 不分组与分组
    '''
    base_factors_df = pd.read_csv(f'{base_dir}/factors.csv')
    if tyeps=="all":
        return base_factors_df
    # 对字段进行拆分并取第二部分作为新的分组列
    base_factors_df['fac_back'] = base_factors_df['feature'].str.split('@').str[0]
    # base_factors_df['fac_back'] = base_factors_df['feature']
    grouped_df = base_factors_df.groupby('fac_back')['feature'].apply(list)
    return grouped_df 

# 初始化csv文件
def init_temp_csv(base_dir):
    df_temp = pd.DataFrame(columns=['total_profit_all','profit_loss','profit_fee','fee','factor_name','is_enter','index',"交易次数"])
    df_factor_temp = pd.read_csv(f'{base_dir}/df_temp.csv')
    # 清空result_temp
    df_temp.drop(df_temp.index, inplace=True)
    df_temp.to_csv(f'{base_dir}/result_tmp.csv',index=False)
    # 清空df_temp
    df_factor_temp.drop(df_factor_temp.index, inplace=True)
    df_factor_temp.to_csv(f'{base_dir}/df_temp.csv',index=False)
    pass