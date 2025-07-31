import numpy as np
import pandas as pd
import os
from typing import Tuple
from typing import Optional
from config import default_data

from statsmodels.graphics.tukeyplot import results

from factor_cal import get_factor_calculator


class DataModule:
    def __init__(self, root_dir: str):
        """
        初始化数据模块
        :param root_dir:数据库的根目录
        """
        self.root_dir = root_dir
    def load_data(
        self,
        instrument: str,
        k_line_type: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
        ) -> pd.DataFrame:
        """
        从本地文件系统加载指定品种和周期的行情数据
        :param instrument: 期货品种代码
        :param k_line_type: k线类型
        :param start_date: 开始日期，格式 'YYYY-MM-DD'
        :param end_date: 结束日期，格式 'YYYY-MM-DD'
        :return: 一个 OHLC 的 DataFrame
        """
        # 构造文件路径
        file_path = os.path.join(
            self.root_dir,
            'data',
            k_line_type,
            instrument,
            f'{instrument}.csv'
        )

        # 检查文件是否存在，并回报错误
        if not os.path.exists(file_path):
            raise FileNotFoundError(f'File not found: {file_path}')

        # 读取CSV文件
        data = pd.read_csv(file_path)

        # 假设原始数据包含以下字段，根据实际字段名调整
        data['datetime'] = pd.to_datetime(data['datetime'])
        data.set_index('datetime', inplace=True)

        # 过滤日期范围
        if start_date:
            data = data[data.index >= pd.to_datetime(start_date)]
        if end_date:
            data = data[data.index <= pd.to_datetime(end_date)]

        # 返回数据集
        return data

class FactorCalculator:
    def __init__(self, factor_to_use=None):
        """
        初始化因子计算器
        :param factor_to_use: 需要使用的因子名称列表，默认使用所有注册的因子
        """
        self.factors_to_use = factor_to_use
        self.available_factors = self._load_available_factors()

    def _load_available_factors(self):
        """
        加载所有可用的因子计算器
        :return: 返回一个包含所有可用因子的字典
        """
        # 从 factor_cal 目录中加载所有因子
        available_factors = {}

        # 获取 factor_cal 目录下的所有 Python 文件
        factor_dir = os.path.dirname(os.path.abspath(__file__))
        for file in os.listdir(factor_dir):
            if file.endswith('.py') and not file.startswith('__'):
                if file.endswith('.py') and not file.startswith('__'):
                    factor_name = file[:-3] # 去掉 .py 后缀

                    # 使用 factor_cal.py 中的 get_factor_calculator 函数
                    factor_class = get_factor_calculator(factor_name)

                    if factor_class:
                        available_factors[factor_name] = factor_class

    def _split_factor_name(self, factor_name):
        """
        对一个因子名称进行分割，考虑两种情况，并返回因子部分和长度部分
        :param factor_name: 需要处理的因子名称
        :return: 返回两个值，一个是因子基础名称的部分，一个是长度部分
        """
        if '@' in factor_name:
            # 对存在长度的因子名称进行分割
            parts = factor_name.split('@')
            if len(parts) == 2:
                factor = parts[0]
                factor_length = int(parts[1])  # 这里对长度进行强制转换
                return factor, factor_length
        # 对没有长度的因子，直接返回结果即可
        return factor_name, None

    def calculate_factors(self, data, instrument, k_line_type, instruments_mindiff):
        """
        应用所有指定因子到数据集上
        :param data: 输入的 OHLC 数据
        :param instrument: 期货品种
        :param k_line_type: K线类型
        :param instruments_mindiff: 品种最小变动单位
        :return: 包含因子的 DataFrame
        """
        # 如果没有指定因子，则使用所有可用的因子
        if not self.factors_to_use:
            self.factors_to_use = list(self.available_factors.keys())

        # 遍历所有需要计算的因子
        for factor_name in self.factors_to_use:
            # 分割因子名称
            factor_base_name, length = self._split_factor_name(factor_name)

            # 检查因子是否可用
            if factor_base_name not in self.available_factors:
                raise ValueError(f'Factor {factor_base_name} is not available.')

            # 获取因子类
            factor_class = self.available_factors[factor_base_name]
            calculator_instance = factor_class()

            # 构建参数
            param = {
                'df': data,
                'instrument': instrument,
                'length': length,
                'k_line_type': k_line_type,
                'mindiff': instruments_mindiff.get(instrument, None),
                'short': default_data["short"],
                'long': default_data["long"],
                'atr_length': default_data["atr_length"],
                'vol_length': default_data["vol_length"],
                'thr': default_data["thr"],
                'n_std': default_data["n_std"],
                'fast': default_data["fast"],
                'slow': default_data["slow"],
                'signal': default_data["signal"],
            }

            # 检查 mindiff 是否存在
            if param['mindiff'] is None:
                print(f'No mindiff found for instrument {instrument}.')
                continue

            # 计算因子
            result = calculator_instance.formula(param)

            # 讲计算结果添加到数据中
            if isinstance(result, pd.DataFrame):
                for col in result.columns:
                    data[col] = result[col]
                else:
                    data[factor_name] = result

        return data



class BacktestEngine:
    def __init__(self, data_module: DataModule, factor_calculator: FactorCalculator):
        """
        初始化回测引擎
        :param data_module: 数据模块实例
        :param factor_calculator: 因子计算器实例
        """
        self.data_module = data_module
        self.factor_calculator = factor_calculator
        self.data = None    # 存储加载并计算因子后的数据

    def load_and_prepare_data(self, instrument: str, k_line_type: str,
                              start_date: Optional[str] = None,
                              end_date: Optional[str] = None):
        """
        加载数据并计算因子
        :param instrument: 期货品种代码
        :param k_line_type: K线类型
        :param start_date: 开始日期
        :param end_date: 结束日期
        :return:
        """
        # 1. 加载原始行情数据
        self.data =  self.data_module.load_data(instrument, k_line_type, start_date, end_date)

        # 2. 获取最小变动单位
        instruments_mindiff = {
            # TODO: 这里要修改成最小变动单位的调用函数
            instrument: 1e-4
        }

        # 3. 计算因子
        self.data = self.factor_calculator.calculate_factors(
            self.data, instrument, k_line_type, instruments_mindiff
        )

    def run_backtest(self, strategy_func):
        """
        运行回测逻辑
        :param strategy_func: 策略函数，接受 DataFrame 返回交易信号
        :return: 包含交易信号和收益的数据集
        """
        if self.data is None:
            raise ValueError('Data has not been loaded.')

        # 1. 应用策略生成交易信号
        signals = strategy_func(self.data)
        self.data['signal'] = signals

        # 2. 模拟下单
        self.execute_order(signals)

        # 3. 更新投资组合状态
        portfolio = self.update_portfolio()

        return portfolio
    def execute_order(self, signal):
        """
        执行订单
        :param signal: 交易信号
        """
        print(f"Executing order with signal: {signal.iloc[-1]}")  # 示例输出最新信号

    def update_portfolio(self):
        """
        更新投资组合状态
        :return: 投资组合状态 DataFrame
        """
        portfolio = pd.DataFrame({
            'positions': [100],  # 持仓数量
            'cash': [5000],  # 可用资金
            'total_value': [10000],  # 总价值
        })
        return portfolio

class PerformanceEvaluator:
    def __init__(self, returns: pd.Series):
        """
        初始化绩效评估器
        :param returns: 包含投资组合收益的 Series
        """
        self.returns = returns

    def calculate_cumulative_return(self) -> float:
        """
        计算累计收益率
        :return: 累计收益率
        """
        cumulative_return = (1 + self.returns).prod() - 1
        return cumulative_return

    def calculate_annualized_return(self) -> float:
        """
        计算年化收益率
        :return: 年化收益率
        """
        num_years = len(self.returns) / 252  # 假设每年有252个交易日
        annualized_return = (1 + self.calculate_cumulative_return()) ** (1 / num_years) - 1
        return annualized_return

    def calculate_volatility(self) -> float:
        """
        计算波动率（年化）
        :return: 波动率
        """
        volatility = self.returns.std() * (252 ** 0.5)
        return volatility

    def calculate_sharpe_ratio(self, risk_free_rate: float = 0.0) -> float:
        """
        计算夏普比率
        :param risk_free_rate: 无风险利率，默认为0.0
        :return: 夏普比率
        """
        excess_returns = self.returns - risk_free_rate / 252  # 调整每日无风险利率
        sharpe_ratio = excess_returns.mean() / self.returns.std() * (252 ** 0.5)
        return sharpe_ratio

    def calculate_max_drawdown(self) -> float:
        """
        计算最大回撤
        :return: 最大回撤值
        """
        cumulative_returns = (1 + self.returns).cumprod()
        rolling_max = cumulative_returns.cummax()
        drawdowns = cumulative_returns / rolling_max - 1
        max_drawdown = drawdowns.min()
        return max_drawdown

    def evaluate_performance(self) -> dict:
        """
        评价回测结果，计算所有绩效指标
        :return: 包含所有绩效指标的字典
        """
        performance_metrics = {
            'Cumulative Return': self.calculate_cumulative_return(),
            'Annualized Return': self.calculate_annualized_return(),
            'Volatility': self.calculate_volatility(),
            'Sharpe Ratio': self.calculate_sharpe_ratio(),
            'Max Drawdown': self.calculate_max_drawdown()
        }
        return performance_metrics


class Main:
    def __init__(self, root_dir: str = '.'):
        """
        初始化整个回测系统的核心模块
        :param root_dir: 数据库根目录，默认为当前路径
        """
        self.root_dir = root_dir
        self.data_module = None
        self.factor_calculator = None
        self.backtest_engine = None
        self.performance_evaluator = None

    def initialize(self):
        """
        初始化各个模块
        :return:
        """

        # 初始化数据模块
        self.data_module = DataModule(root_dir=self.root_dir)

        # 初始化因子计算器（可以指定使用哪些因子）
        self.facotor_calculator = FactorCalculator(factor_to_use=[
            ''
        ])

        # 初始化回测引擎
        self.backtest_engine = BacktestEngine(
            data_module=self.data_module,
            factor_calculator=self.factor_calculator
        )

    def run_backtest(self, instrument:str, k_line_type: str,
                     start_date: Optional[str] = None,
                     end_date: Optional[str] = None):
        """
        运行回测
        :param instrument: 交易标的
        :param k_line_type: K 线类型
        :param start_date: 开始日期
        :param end_date: 结束日期
        :return: 包含结果的 DataFrame
        """
        if not self.backtest_engine:
            raise ValueError('Backtest engine has not been initialized.')

        # 加载并准备数据（包含因子计算）
        self.backtest_engine.load_and_prepare_data(
            instrument, k_line_type, start_date, end_date
        )

        # 如果没有传入策略函数，则使用默认策略
        if strategy_func is None:
            def default_strategy(data):
                # 示例：基于均线的简单策略
                short_window = 5
                long_window = 20
                data['short_ma'] = data['close'].rolling(short_window).mean()
                data['long_ma'] = data['close'].rolling(long_window).mean()

                data['signal'] = 0
                data.loc[data['short_ma'] > data['long_ma'], 'signal'] = 1  # 做多信号
                data.loc[data['short_ma'] <= data['long_ma'], 'signal'] = -1  # 做空信号
                return data['signal']

            strategy_func = default_strategy

        # 执行回测
        result_df = self.backtest_engine.run_backtest(strategy_func)

        # 返回回测结果
        return result_df

    def evaluate_results(self, returns_series: pd.Series):
        """
        使用 PerformanceEvaluator 对收益进行绩效分析
        :param returns_series: 收益率 Series
        """
        self.performance_evaluator = PerformanceEvaluator(returns=returns_series)
        performance_metrics = self.performance_evaluator.evaluate_performance()

        print("📊 回测绩效指标如下：")
        for metric, value in performance_metrics.items():
            print(f"{metric}: {value:.4f}")

    def start(self):
        """
        启动完整的回测流程（示例运行）
        """
        instrument = 'rb'  # 示例交易标的
        k_line_type = '1D'  # 日K线
        start_date = '2023-01-01'
        end_date = '2024-01-01'

        print(f"🚀 开始回测 {instrument} ({k_line_type}) 从 {start_date} 到 {end_date}")
        result_df = self.run_backtest(instrument, k_line_type, start_date, end_date)

        # 提取策略收益率
        if 'strategy_returns' in result_df.columns:
            returns = result_df['strategy_returns']
        else:
            # 若未生成策略收益，模拟一个
            result_df['strategy_returns'] = result_df['close'].pct_change().shift(-1)
            returns = result_df['strategy_returns']

        print("✅ 回测完成，开始评估绩效...")
        self.evaluate_results(returns)

        return result_df