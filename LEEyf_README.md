# LEEyf分支说明文件

这里是李亦凡的分支，用于保存回测相关的程序。

## 更新日志

### 2025-06-18	回测框架的搭建

#### 2025-06-20

- 利用 AI 简单搭建了一个因子回测的框架，具体的内容以及实现方法还要慢慢研究。数据回测框架大致的结构包括：数据载入、因子计算器载入、回测主体部分、回测表现评测、主函数运行。
- DataModule：直接调用 data 中的数据，构建一个数据集，供后续回测使用:
  - load_data: 通过文件路径调用数据库中的数据
  - root_dir: 文件的根目录
- FactorCalculator：调用 factor_cal 中的因子计算器，进行因子计算器的准备:
  - _load_available_factors: 加载所有可用的因子计算器
  - _split_factor_name: 对一个因子名称进行分割
  - calculate_factors: 对因子进行计算
- BacktestEngine: 回测引擎
  - load_and_prepare_data: 加载数据并计算因子
  - run_backtest: 运行回测逻辑
  - execute_order: 执行订单
  - update_portfolio: 更新投资组合状态
- PerformanceEvaluator: 回测评估

