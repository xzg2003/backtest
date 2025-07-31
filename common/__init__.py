"""
通用工具模块

该模块包含量化交易回测系统中使用的各种通用工具函数和辅助类，
为整个系统提供基础支持功能。

Submodules
----------
util : 模块
    提供文件操作、目录管理、数据保存和加载等基础工具函数

data_common : 模块
    提供交易日历查询、合约信息查询等数据访问功能

back_test_common : 模块
    提供回测过程中使用的通用函数，如唯一ID生成等

bt_common : 模块
    提供回测流程中的专用工具函数，如因子数据处理等

主要功能
--------
1. 文件和目录操作
2. 数据序列化和反序列化
3. 交易日查询和时间计算
4. 回测流程辅助工具
5. 因子数据预处理工具

使用示例
--------
    import common.util as zutil
    zutil.mkdir('./new_directory')

    from common.data_common import Data_Common
    data_common = Data_Common.create_instance()

    from common.back_test_common import generate_unique_string
    unique_id = generate_unique_string()

该模块为整个回测系统提供底层支持，所有工具函数都设计为可重用和无副作用。
"""