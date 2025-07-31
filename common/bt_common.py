"""
回测公共方法模块
包含回测过程中使用的各种通用函数和工具方法
"""

import pandas as pd


# 拷贝一份base_factors 到factors
# 然后删除factors 里面包含enter的行
# get_group_df 直接读取删除后的数据
def delete_enter_4_base(base_dir):
    """
    从基础因子中删除与入场信号相关的因子

    该函数读取基础因子文件和入场信号文件，将存在于入场信号文件中的因子
    从基础因子中移除，并将结果保存为新的因子文件。

    Parameters
    ----------
    base_dir : str
        基础目录路径，包含基础因子和入场信号文件
    """
    # 读取基础因子数据
    base_factors_df = pd.read_csv(f'{base_dir}/base_factors.csv')

    # 读取入场信号数据
    enter_df = pd.read_csv(f'{base_dir}/enter.csv')

    # 合并两个数据框，找出仅在基础因子中存在的因子（即需要保留的因子）
    df_c = pd.merge(enter_df, base_factors_df, on='feature', how='outer', indicator=True)
    df_c = df_c[df_c['_merge'] == 'right_only']
    df_c = df_c.drop('_merge', axis=1)

    # 将处理后的因子数据保存到factors.csv文件
    df_c.to_csv(f'{base_dir}/factors.csv', index=False)


def get_group_df(base_dir, types="group"):
    """
    获取分组后的因子数据框

    该函数读取因子数据，并根据指定类型返回全部因子或分组后的因子

    Parameters
    ----------
    base_dir : str
        基础目录路径，包含因子文件
    types : str, optional
        数据返回类型，"all"表示返回全部因子，"group"表示返回分组因子，默认为"group"

    Returns
    -------
    pandas.DataFrame or pandas.Series
        如果tyeps为"all"，返回全部因子的DataFrame；
        如果tyeps为"group"，返回按因子前缀分组的Series，索引为因子前缀，值为因子列表
    """
    # 读取因子数据
    base_factors_df = pd.read_csv(f'{base_dir}/factors.csv')

    # 如果类型为"all"，直接返回全部因子数据
    if types == "all":
        return base_factors_df

    # 对字段进行拆分并取第二部分作为新的分组列
    # 例如将"FCT_RSI@5"拆分为"FCT_RSI"作为分组依据
    base_factors_df['fac_back'] = base_factors_df['feature'].str.split('@').str[0]

    # base_factors_df['fac_back'] = base_factors_df['feature']

    # 按照因子前缀进行分组，将同一前缀的因子组合成列表
    grouped_df = base_factors_df.groupby('fac_back')['feature'].apply(list)

    return grouped_df


def init_temp_csv(base_dir):
    """
    初始化临时CSV文件

    该函数创建并清空用于存储回测结果的临时CSV文件

    Parameters
    ----------
    base_dir : str
        基础目录路径，包含临时文件
    """
    # 创建结果临时数据框的列结构
    df_temp = pd.DataFrame(columns=[
        'total_profit_all',  # 总利润
        'profit_loss',  # 盈亏因子
        'profit_fee',  # 费率比（利润/手续费）
        'fee',  # 手续费
        'factor_name',  # 因子名称
        'is_enter',  # 是否为入场信号
        'index',  # 索引
        "交易次数"  # 交易次数
    ])

    # 读取现有的临时数据框文件
    df_factor_temp = pd.read_csv(f'{base_dir}/df_temp.csv')

    # 清空结果临时文件内容
    df_temp.drop(df_temp.index, inplace=True)
    df_temp.to_csv(f'{base_dir}/result_tmp.csv', index=False)

    # 清空因子临时文件内容
    df_factor_temp.drop(df_factor_temp.index, inplace=True)
    df_factor_temp.to_csv(f'{base_dir}/df_temp.csv', index=False)

    pass
