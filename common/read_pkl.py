"""
Pickle文件读取模块
用于读取和分析序列化的pandas DataFrame数据文件
"""

# 读取文件(不压缩)

import os
import sys

sys.path.append(os.getcwd())
import common.util as zutil

# 默认文件路径
# TODO：这个文件路径无法找到，是否应该设计一个新的目录？
file_path = './data/fundamental/A/A1009/FCT_basis_diff_ma_sec@3.pkl'


# 2023-04-08 01:10:00
def load_file(file_path):
    """
    加载并分析pickle格式的文件

    该函数读取指定路径的pickle文件，进行基本统计分析，并将数据保存为CSV格式

    Parameters
    ----------
    file_path : str
        要读取的pickle文件路径

    Returns
    -------
    pandas.DataFrame
        从pickle文件加载的数据
    """
    # 记录开始时间，用于性能统计
    t = zutil.Calc_Time("load_file")

    # 使用工具函数加载pickle文件
    df = zutil.load_file(file_path)

    # print(f"总数:  {len(df)}")
    # print(f">0:  {len(df[df['ret.24']>0])}")
    # print(f"<0:  {len(df[df['ret.24']<0])}")
    # print(f"=0:  {len(df[df['ret.24']==0])}")

    # df.head(100).to_csv('test.csv')
    # df = df['ma_selected3_24'].copy()

    # 将数据保存为CSV文件用于查看
    df.to_csv('test.csv')
    # print(len(df))
    # print(df.columns)
    # 保持列名
    # df.columns.to_series().to_csv('column_names.txt', index=False)

    # 输出执行时间统计
    t.t()
    return df


if __name__ == "__main__":
    """
    程序入口点
    支持命令行参数传入文件路径，否则使用默认路径
    """
    print("传入参数，即读取参数传入的文件路径的文件，否则在代码中修改文件路径")
    print("python csgo_common/read_pkl.py [file_path]")

    # 获取命令行参数
    args = sys.argv

    # 根据参数数量决定使用传入路径还是默认路径
    if len(args) == 2:
        file_path = args[1]
        print(file_path)
        load_file(file_path)
    else:
        load_file(file_path)

    pass
