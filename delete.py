# 删除期货因子的代码，万一大家算出来的因子有问题可以删了重新算
import os
import csv

from config import instruments
from config import k_line_types


def delete_all_factors_except_main():
    """
    删除所有因子文件，只保留主数据文件
    """
    k_lines = k_line_types

    for k_line in k_lines:
        print(f"处理 {k_line} 类型数据...")
        for instrument in instruments:
            dir_path = f'./data/{k_line}/{instrument}'
            if not os.path.exists(dir_path):
                continue

            # 遍历目录中的所有文件
            for file_name in os.listdir(dir_path):
                file_path = os.path.join(dir_path, file_name)

                # 只删除不是主数据文件的CSV文件
                if file_name.endswith('.csv') and file_name != f"{instrument}.csv":
                    try:
                        os.remove(file_path)
                        print(f'已删除：{file_path}')
                    except Exception as e:
                        print(f'删除失败 {file_path}: {e}')
                elif file_name == f"{instrument}.csv":
                    print(f'保留主数据文件：{file_path}')


if __name__ == '__main__':
    print("即将删除所有因子文件，只保留主数据文件")
    confirm = input("此操作不可恢复，输入yes确认执行：")

    if confirm.lower() == 'yes':
        delete_all_factors_except_main()
        print("删除完成。")
    else:
        print("操作已取消。")
