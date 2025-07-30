# 交易回撤 绩效
# 1，总利润：分多头利润，空头利润，（完成）
# 2，盈利因子：所有总盈利/所有交易的总亏损，分多头盈利因子和空头盈利因子，（完成）
# 3，交易次数，分多头交易次数和空头交易次数，（完成）
# 4，权益最大回撤，（完成）
# 5，夏普率，（完成，待确认）
# 6，费率比：总利润/总佣金（完成）
# 7，资产曲线和回撤曲线（待开发）
# 8，阶段总结：以上数据的分年度统计（待处理）


# 因子： 威廉、动量、KDJ、MACD、DMI、乖离、持仓量、成交量、
#  基本上5个参数


import base64
import json
import multiprocessing
import os
import pandas as pd
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt


import matplotlib
# # 设置中文字体
zh_font = matplotlib.font_manager.FontProperties(fname="Arial_Unicode_MS.ttf")

from dotenv import dotenv_values
env_vars = dotenv_values(".env")
import os
import sys
sys.path.append(os.getcwd())
import common.util as zutil
from  common.data_common import Data_Common
from config import *
# 获取当前日期
current_date = datetime.now()
# 生成字符串格式
date_string = current_date.strftime("%Y-%m")
#base_file_store_path = env_vars['file_store_path']
base_file_store_path = '.'

file_store_path = os.path.join(base_file_store_path,date_string)
zutil.mkdir(f"{base_file_store_path}/images/")
zutil.mkdir(f'{zutil.file_store_path}/json/')

# 创建文件夹
def mkdir(path):
    if not os.path.exists(path):
        os.makedirs(path)

mkdir(file_store_path)


# 定义多空买卖
BUY =1
SELL =-1
OPEN=0
CLOSE=1
FEE_FEE=0.0002

class Performance():
    def __init__(self,param):
        self.obj={}
        self.obj['total_profit']=0
         # 开始时间
        self.start_time = int(param['st'])
        # 结束时间
        self.end_time = int(param['et'])
        print(f"startTime::{param['st']}:::endTime::{param['et']}")
        self._cal_years()
        # 初始金额
        self.initial_value = param["initial_value"]
        self.risk_free_rate = param["risk_free_rate"]  # 无风险利率
        # 总佣金
        self.commission=param["commission"]
        # 跨越的年数
        # self.years=3
        # self._cal_years()
        self.other_text = param["next_text"]
        time_p = datetime.now().strftime("%Y-%m-%d_%H_%M_%S")
        # 为生成html 文件名
        self.image_path= time_p
        self.html_name = f'{time_p}'
        self.data_common = Data_Common.create_instance()

        self.ins_list = instruments
        self.model_flag = 'pre_1'
        self.df_data={}
        self.data_common = Data_Common.create_instance()
        # 持仓记录
        self.equity_order=pd.DataFrame(columns=['date','order_date','trading_date','instrument_id','instrument','buyOrSell','openOrClose','price','openPrice',
                                                'count','count_back','ID','tradeId','mul','flag','model_flag','status','fee','pre_price','current_price'])
        # 每日持仓统计
        self.daily_df = pd.DataFrame(columns=["date",'profit','model_flag','fee','long_fee','short_fee','profit_all',
                                              'profit_float','rate','sum_profit','sum_rate','sum_long_profit','sum_short_profit'])
        # 订单表
        self.order_df = zutil.load_file("./data/order.pkl")


    def get_instruments(self):
        instruments_list=[]
        info = self.data_common.get_futures_mul()
        for idx,item in info.iterrows():
            instruments_list.append(item['instrument'])
        return instruments_list

    # 计算日期年数
    def _cal_years(self):
        start = datetime.strptime(str(self.start_time), "%Y%m%d")
        end = datetime.strptime(str(self.end_time), "%Y%m%d")
        delta = end - start
        if delta.days==0:
            years_diff =round(1/365,3)
        else:
            years_diff = round(delta.days/365,3)

        self.years = years_diff
        print("self.years:::",self.years)
    
    # 获取某个时间段内的数据
    def get_data(self,instrument=""):
        st  = datetime.strptime(str(self.start_time), "%Y%m%d").strftime("%Y-%m-%d")
        et= datetime.strptime(str(self.end_time), "%Y%m%d").strftime("%Y-%m-%d")
        #st = self.start_time
        #et = self.end_time(self.order_df['trading_date']>=st)&
        #print(self.order_df[(self.order_df['instrument']==instrument)])
        if instrument =="":
            df =self.order_df[(self.order_df['model_flag']==self.model_flag) & (self.order_df['trading_date']>=st) & (self.order_df['trading_date']<=et)]
            return df 
        else:
            df =self.order_df[(self.order_df['model_flag']==self.model_flag) &  (self.order_df['instrument']==instrument)]
            return df
        
    # 总利润
    # # 1，总利润：分多头利润，空头利润，
    def profit(self):
        self.obj['long_df_fee'] =0
        self.obj['short_df_fee'] =0
        for item in self.ins_list.copy():
            ins = item
            df = self.get_data(ins).copy()
            # 开多是long 开空是short
            # filtered_df = df[df['buyOrSell'] == 1]
            if len(df)==0:
                print('没有从数据库中找到匹配的数据::',ins)
                self.ins_list.remove(ins)
                continue
            df['fee'] = df['price']*df['count']*df['mul']*FEE_FEE
            
            self.obj[ins]={}
            # 开多利润
            long_df = df[(df['buyOrSell'] == BUY) & (df['openOrClose']==CLOSE)]
            long_df_fee = df[df['buyOrSell'] == BUY]['fee'].sum()
            self.obj[ins]["long_profit"] = ((long_df['price'] -long_df['openPrice'])*long_df['mul']*long_df['count']).sum()
            self.obj[ins]['long_profit'] -=long_df_fee
            self.obj['long_df_fee'] +=long_df_fee
            
            # 开空利润
            short_df =  df[(df['buyOrSell'] == SELL) & (df['openOrClose']==CLOSE)]
            short_df_fee = df[df['buyOrSell'] == SELL]['fee'].sum()
            self.obj[ins]["short_profit"] = ((short_df['price'] -short_df['openPrice'])*short_df['mul']*short_df['count']*SELL).sum()
            self.obj[ins]['short_profit'] -= short_df_fee
            self.obj['short_df_fee'] +=short_df_fee

            # 多空总利润
            self.obj[ins]['total'] = self.obj[ins]['long_profit']+self.obj[ins]['short_profit']
            # 总盈利不需要计算每天的浮盈
            self.obj['total_profit'] +=self.obj[ins]['total']

        self.obj['total_rate'] = self.obj['total_profit'] /self.initial_value  /self.years


    def long_or_short_factors(self,df_temp):
        profit=0
        loss =0
        df = df_temp.copy()
        df['profit_res'] = (df['price'] - df['openPrice'])*df['openOrClose']*df['buyOrSell']*df['mul']*df['count']
        profit = df[df['profit_res']>0]["profit_res"].sum()
        loss = df[df['profit_res']<=0]["profit_res"].sum()
        return profit,loss
    
    # 2，盈利因子：所有总盈利/所有交易的总亏损，分多头盈利因子和空头盈利因子，
    def profit_factor(self):
        self.obj['factor'] = {}
        df = self.get_data().copy()
        # 多头
        long_df = df[df['buyOrSell'] == BUY]
        # 交易次数
        self.obj['long_trade_count'] = (long_df['openOrClose'] == CLOSE).sum()
        self.obj['factor']['long_profit'],self.obj['factor']['long_loss'] = self.long_or_short_factors(long_df)
        
        # 空头
        short_df =  df[df['buyOrSell'] == SELL]
        self.obj['short_trade_count'] = (short_df['openOrClose'] == CLOSE).sum()
        self.obj['factor']['short_profit'],self.obj['factor']['short_loss'] =self.long_or_short_factors(short_df)
        
        # 总交易次数
        self.obj['all_trade_count'] = (df['openOrClose']==CLOSE).sum()

        self.obj['factor']['total_profit'] = self.obj['factor']['long_profit'] + self.obj['factor']['short_profit']
        self.obj['factor']['total_loss']= self.obj['factor']['long_loss'] + self.obj['factor']['short_loss']

        if self.obj['factor']['total_loss']==0:
            self.obj['factor']['rate']=0
        else:
            self.obj['factor']['rate'] = self.obj['factor']['total_profit']/self.obj['factor']['total_loss']

        print(f"self.obj['factor']::{self.obj['factor']}")
        

    # 3，交易次数，分多头交易次数和空头交易次数，放到上面去计算了
    
    # 4，权益最大回撤，(按天计算 每日资金=（平仓利润+浮盈浮亏+初始资金）/初始资金)

    # 数据库计算每日的平仓利润+持仓信息
    def insert_daily_equity(self):
        daily = self.data_common.get_trading_days(self.start_time,self.end_time)
        # daily_datas = list(daily) 
        # 遍历结果
        pre_day =0
        for idx,doc in daily.iterrows():
            # print(doc)
            date = int(doc["date"].strftime("%Y%m%d"))
            if date==self.start_time:
                pre_day = self.start_time
            self.get_daily_records(date,pre_day)
            pre_day = date
        return

    
    # 计算每天的数据
    # 1、通过record表 找到今天的交易记录和前一天持仓记录
    # 2、根据今天的交易记录，处理今天的持仓记录
    # 3、判断前一天的持仓记录，如果昨天的持仓为空，则今天的持仓直接为第2步的持仓
    # 4、如果前一天的持仓不为空，先移除昨天持仓的count为0的数据，再合并今天和前一天的持仓，处理ID重复数据的count
    # 5、更新今天持仓的所有品种的今日价格
    def get_daily_records(self,date,pre_day):
        # print(f"get_daily_records:: {date} ")
        # 查询今天的记录
        # st,et = bt_common.get_trading_day(date)
        date = datetime.strptime(str(date), '%Y%m%d').strftime('%Y-%m-%d')
        # 查询今天的开仓记录,将开仓记录直接放入前一天的记录中
        self.order_df['datetime'] = pd.to_datetime(self.order_df['datetime'])
        res_open = self.order_df[(self.order_df['model_flag']==self.model_flag) & (self.order_df['trading_date']==date) & (self.order_df['openOrClose']==OPEN)].sort_values(by="datetime")
        open_list = res_open.to_dict(orient='records')
        # 查询今天的平仓记录，判断开仓中是否有平仓
        res_close = self.order_df[(self.order_df['model_flag']==self.model_flag) & (self.order_df['trading_date']==date) & (self.order_df['openOrClose']==CLOSE)].sort_values(by="datetime")
        close_list = res_close.to_dict(orient='records')


        # docs_list = list(res)
        param={}
        param['date'] = date
        # 利润
        param['profit']=0
        # 持仓
        param['equity']=[]

        pre = ""
        pre_equity=[]
        if len(self.daily_df)==0:
            pre = None
        else:
            pre_day = datetime.strptime(str(pre_day), '%Y%m%d').strftime('%Y-%m-%d')
            pre_equity_df = self.equity_order.loc[(self.equity_order['date']==pre_day) & (self.equity_order['model_flag'] == self.model_flag)]
            if len(pre_equity_df)>0:
                for idx,item in pre_equity_df.iterrows():
                    pre_equity.append(item.to_dict())

        if pre is None or len(pre_equity)==0:
            param['equity']= open_list
        else:
            param['equity'] = pre_equity.copy()
            param['equity'].extend(open_list)
        
        # 查找昨天到记录里面是否有count=0的数据，移除前一天的=0数据
        for item in param['equity'].copy():
            if item['count'] ==0:
                param['equity'].remove(item)

        # 判断open 和close 是否有重复的ID
        for open_item in param['equity']:
            open_flag = False
            current_price = self.get_current_price(date,open_item['instrument'].upper())
            if current_price ==0:
                current_price = open_item['price']
                print(f"current price is none ,data is loss... {open_item['instrument']}-{open_item['date']}")
            for close_item in close_list:
                if open_item["ID"] == close_item['ID']:
                    open_item['count'] = close_item['count'] - open_item['count']
                    # if open_item['count']==0 and  bt_common.get_current_day(open_item['date']) == bt_common.get_current_day(close_item['order_date']):
                    if open_item['count']==0 and  open_item['trading_date'] == close_item['trading_date']:
                        current_price = close_item['price']
                        open_item['price'] =  current_price
                    else:
                        open_item['price'] = close_item['price']
                        if "pre_price"  in open_item:
                            open_item['openPrice'] =  open_item['pre_price']
                        else:
                            print(f"{open_item['instrument']} -- {open_item['date']} -- {open_item['order_date']}")
                            pass
                        
                        
                    open_item['current_price'] = current_price
                    open_item['pre_price'] = current_price
                    open_item['open_date'] = open_item['trading_date']
                    open_flag = True
                    
            if open_flag == False:
                if "pre_price"  in item and 'current_price' in item:
                    open_item['openPrice'] = open_item['pre_price']
                else:
                    open_item['openPrice'] =  open_item['price']
                
                open_item['pre_price'] = current_price
                open_item['price'] =  current_price
                open_item['current_price'] = current_price
        
        param['model_flag'] = self.model_flag
        if len(param['equity'])>0:
            for item in param['equity']:
                item['date'] = date
                self.equity_order.loc[len(self.equity_order)]= item
        daily_p = param.copy()
        
        del daily_p['equity']
        self.daily_df.loc[len(self.daily_df)] = daily_p

    def get_base_data_info(self,instrument):
        if instrument not in self.df_data:
            data_path = f'{DATA_DIR}/{k_line_type}/{instrument}'
            df = pd.read_csv(f'{data_path}/{instrument}.csv')
            if 'date' in df.columns:
                df.rename(columns={'date': 'datetime'}, inplace=True)
                df['trading_date'] = df['datetime']
            self.df_data[instrument] = df
        return self.df_data[instrument]
    
     # 获取今天的收盘价
    def get_current_price(self,date,instrument):
        end_date = date
        base_df = self.get_base_data_info(instrument)
        current_price = base_df[base_df['trading_date']==end_date].sort_values(by="datetime")
        if len(current_price)==0:
            print("current_price is none:::::",date,instrument,end_date)
            return 0
        return current_price.iloc[-1]['close']
    
    # 计算每天的收益 profit_float profit_all
    def calc_profit_float_and_all(self):
        equity_list = self.daily_df[self.daily_df['model_flag']==self.model_flag].sort_values(by='date')
        sum_profit=0
        for idx,doc in equity_list.iterrows():
            profit_float= 0
            profit_all=0
            fee = doc['fee']
            orders = self.equity_order[self.equity_order['date']==doc['date']]
            for i,item in orders.iterrows():
                profit_float += ((item['price']-item['openPrice'])*item['count_back'])*item['mul']*item['buyOrSell']
            # 统计的盈利减去每日的手续费，是每日的实际盈利
            profit_all  += (profit_float-fee)
            sum_profit +=profit_all
            # rate =(profit+profit_float+本金)/本金 -1
            rate = ((profit_all+self.initial_value)/self.initial_value-1)*100
            sum_rate =  ((sum_profit+self.initial_value)/self.initial_value-1)*100
            self.daily_df.loc[idx,['profit_float','profit_all','rate','sum_profit','sum_rate']]=[profit_float,profit_all,rate,sum_profit,sum_rate]

    # 计算每天的多空收益 需要去除手续费
    def calc_profit_float_long_and_short(self):
        equity_list = self.daily_df[self.daily_df['model_flag']==self.model_flag].sort_values(by='date')
        sum_long_profit=0
        sum_short_profit=0
        for idx,doc in equity_list.iterrows():
            long_profit= 0
            short_profit=0
            long_fee =doc['long_fee']
            short_fee =doc['short_fee']
            orders = self.equity_order[self.equity_order['date']==doc['date']]
            for i,item in orders.iterrows():
                if item['buyOrSell'] == BUY:
                    long_profit += ((item['price']-item['openPrice'])*item['count_back'])*item['mul']*item['buyOrSell']
                else:
                    short_profit += ((item['price']-item['openPrice'])*item['count_back'])*item['mul']*item['buyOrSell']
            # 统计的盈利减去每日的手续费，是每日的实际盈利
            
            sum_long_profit +=  (long_profit-long_fee)
            sum_short_profit += (short_profit-short_fee)

            self.daily_df.loc[idx,['sum_long_profit','sum_short_profit',]]=[sum_long_profit,sum_short_profit]

    # 计算最大回撤
    def calc_max_drawdown(self):
        # 按日期排序上面的rate
        rate_list = self.daily_df[self.daily_df['model_flag']==self.model_flag].sort_values(by="date")
        rate_data = rate_list['sum_rate'].to_numpy()

        peak = rate_data[0]
        drawdown = 0
        max_drawdown = 0
        
        for r in rate_data:
            if r > peak:
                peak = r
                drawdown = 0
            else:
                drawdown = peak - r
                if drawdown > max_drawdown:
                    max_drawdown = drawdown
        # print(max_drawdown)
        self.obj['max_drawdown'] = max_drawdown

    # 5，夏普率，

    # 获取资产总价值 初始金额+总盈利
    def get_total_value_and_rate(self):
        rate_list = self.daily_df[self.daily_df['model_flag']==self.model_flag].sort_values(by="date")
        rate_data = rate_list['rate'].to_numpy()
        return rate_data


    # 计算夏普率函数
    def sharpe_ratio(self):
        radical250=15.811
        # TODO 构造了一个假数据 obj['annualized_return']+100
        returns = np.array( self.get_total_value_and_rate())
        # excess_returns = returns - self.risk_free_rate
        # mean_excess_return = np.mean(excess_returns)
        std_deviation = np.std(returns)
        # print("mean_excess_return:::",mean_excess_return)
        print("std::",std_deviation)

        # 年化收益率:{round(self.obj["total_rate"]*100,2)}%
        years_rate = self.obj["total_rate"] 

        sharpe_ratio = (years_rate -self.risk_free_rate) / (std_deviation *radical250)

        self.obj['sharpe_ratio'] = sharpe_ratio * 100 
        print(f"sharpe_ratio::{self.obj['sharpe_ratio']}")
        self.obj['sharpe_ratio'] = round(self.obj["sharpe_ratio"],2)

    def calc_rate_ratio(self):
        # 费率比 # 6，费率比：总利润/总佣金（完成）
        # 期货公司的佣金（张总说的，2023-10-04）
        rateRatio = (self.obj['total_profit'])/ self.obj['fee']
        self.obj['rateRatio'] = rateRatio

    # 7，资产曲线和回撤曲线
    def draw_plt(self):
        # data = daily_equity_conllection.find({'$and':[{'date':{'$gte':self.start_time}},{'date':{'$lte':self.end_time}}]})
        data = self.daily_df[self.daily_df['model_flag']==self.model_flag]
        x=[]
        # y=[]
        # y2=[]
        y3=[]
        y4=[]
        y5=[]
        x_date=[]
        for idx,item in data.iterrows():
        # 将日期字符串转换为datetime对象
            date = datetime.strptime(str(item['date']), '%Y-%m-%d')
            x_date.append(datetime.strptime(str(item['date']), '%Y-%m-%d').strftime("%Y-%m-%d"))
            x.append(date)
            
            y3.append(item['sum_long_profit']/self.initial_value)
            y4.append(item['sum_short_profit']/self.initial_value)
            y5.append(item['sum_profit']/self.initial_value)
        self._draw_plt(x,y5,y3,y4,'收益曲线','日期','收益率',f'{base_file_store_path}/images/{self.image_path}_3.png')
        x_date_file=["date"]
        y3_file=['sum_long_profit']
        y4_file=['sum_short_profit']
        y5_file=['sum_profit']
        x_date_file.extend(x_date)
        y3_file.extend(y3)
        y4_file.extend(y4)
        y5_file.extend(y5)
        self.write_list_to_json(x_date_file,f'{zutil.file_store_path}/json/{self.image_path}_date.json')
        self.write_list_to_json(y3_file,f'{zutil.file_store_path}/json/{self.image_path}_sum_long_profit.json')
        self.write_list_to_json(y4_file,f'{zutil.file_store_path}/json/{self.image_path}_sum_short_profit.json')
        self.write_list_to_json(y5_file,f'{zutil.file_store_path}/json/{self.image_path}_sum_profit.json')

    def write_list_to_json(self,my_list,file_name):
        with open(file_name, 'w') as f:
            json.dump(my_list, f)
        pass

    def _draw_plt(self,x,y,y3,y4,title,xlabel,ylabel,save_file):
        
        # 创建图表对象,figsize 控制图片大小
        fig, ax = plt.subplots(figsize=(16, 8))
        
        # 绘制曲线图
        ax.plot(x, y)
         # 绘制第二根曲线
        if len(y3)>0:
            ax.plot(x, y3, color='red', label='y2',alpha=0.7)
        if len(y4)>0:
            ax.plot(x, y4, color='green', label='y3',alpha=0.6)

        # 添加标题和标签
        plt.title(title, fontproperties=zh_font)
        plt.xlabel(xlabel, fontproperties=zh_font)
        plt.ylabel(ylabel, fontproperties=zh_font)
       
       # 设置x轴刻度
        st =datetime.strptime(str(self.start_time), '%Y%m%d').strftime('%Y-%m')
        et = datetime.strptime(str(self.end_time), '%Y%m%d').strftime('%Y-%m')
        # custom_ticks = np.arange(st,et, dtype='datetime64[M]')
        custom_ticks = np.arange(st,et,step=np.timedelta64(6, 'M'),  dtype='datetime64[M]')
        plt.xticks(custom_ticks)

        # 自动调整日期显示格式
        fig.autofmt_xdate()
        # 显示网格
        ax.grid(alpha=0.3)
       
        # 显示图形
        plt.savefig(save_file)
        #plt.show()

        # self.write_text_in_pic(save_file)
    # 将图片转化为base64
    def image_to_base64(self,image_path):
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
        return encoded_string

    def draw_single(self,data,ins,initial_value):
        x=[]
        y3=[]
        y4=[]
        y5=[]
        for item in data:
            # 将日期字符串转换为datetime对象
            date = datetime.strptime(str(item['date']), '%Y%m%d')
            x.append(date)
            y3.append(item[ins]['sum_long_profit']/initial_value)
            y4.append(item[ins]['sum_short_profit']/initial_value)
            y5.append(item[ins]['sum_profit']/initial_value)
        self._draw_plt(x,y5,y3,y4,f'{ins}--收益曲线','日期','收益率',f'{base_file_store_path}/images/{self.image_path}_{ins}.png')
        pass
    # 将obj 对象写入文件中
    def json_2_file(self):
        
        image3 = self.image_to_base64(f'{base_file_store_path}/images/{self.image_path}_3.png')
        
        long_profit = self.obj["factor"]["long_profit"]+self.obj["factor"]["long_loss"]-self.obj["long_df_fee"]
        short_profit = self.obj["factor"]["short_profit"]+self.obj["factor"]["short_loss"]-self.obj["short_df_fee"]
        with open(f'{file_store_path}/{self.html_name}.html', 'w', encoding='utf-8') as file:
            file.write('<html>\n')
            file.write(f'<head><meta charset="UTF-8"><title>{self.html_name}</title>\n')
            file.write('<script type="text/javascript" src="../static_js/echarts.min.js"></script> \n')
            file.write('<script type="text/javascript" src="../static_js/jquery.min.js"></script> \n')
            file.write('<script type="text/javascript" src="../static_js/base.js"></script> \n')
            file.write('<script type="text/javascript">var date_set=[]; \n')
            file.write('$.when( \n')
            file.write(f'$.getJSON("../json/{self.image_path}_date.json"), \n')
            file.write(f'$.getJSON("../json/{self.image_path}_sum_profit.json"), \n')
            file.write(f'$.getJSON("../json/{self.image_path}_sum_long_profit.json"), \n')
            file.write(f'$.getJSON("../json/{self.image_path}_sum_short_profit.json") \n')
            file.write(').then(function(data1, data2, data3,data4) { \n')
            file.write('date_set.push(data1[0]);date_set.push(data2[0]);date_set.push(data3[0]);date_set.push(data4[0]); \n')
            file.write('run(date_set);}).fail(function() { \n')
            file.write('});</script> \n')

            file.write('</head><body style="height: 100%; margin: 20px">\n')
            file.write(f'<img src="data:image/jpeg;base64,{image3}">\n')
            if self.obj["factor"]["long_loss"]==0:
                long_factore = 0
            else:
                long_factore =round(abs(self.obj["factor"]["long_profit"]/self.obj["factor"]["long_loss"]),2)
            
            if self.obj["factor"]["short_loss"]==0:
                short_factore =0
            else:
                short_factore = round(abs(self.obj["factor"]["short_profit"]/self.obj["factor"]["short_loss"]),2)

            if self.obj["max_drawdown"]==0:
                fl = 0
            else:
                fl = round(self.obj["total_rate"]/self.obj["max_drawdown"]*100,2)

            if self.other_text is not None or self.other_text !="":
                file.write(f'<div sytle="color:red">{self.other_text}</div> </br>')
            file.write('<div>')
            file.write(f'本金{self.initial_value} | 年化收益率:{round(self.obj["total_rate"]*100,2)}% | 总收益:{round(self.obj["total_profit"],2)} | 费率比:{round(self.obj["rateRatio"],2)}| 最大回撤:{round(self.obj["max_drawdown"],2)}%|风险收益比: {fl}  |夏普：{self.obj["sharpe_ratio"]} </br> ')
            file.write(f'总交易次数: {self.obj["all_trade_count"]} | 多头次数: {self.obj["long_trade_count"]} | 空头次数: {self.obj["short_trade_count"]} </br> ')
            file.write(f'多头盈利: {self.obj["factor"]["long_profit"]} | 多头损失: {self.obj["factor"]["long_loss"]} | 空头盈利: {self.obj["factor"]["short_profit"]} | 空头损失: {self.obj["factor"]["short_loss"]} (本行统计不含手续费)</br> ')
            file.write(f'多头盈利: {self.obj["long_win_profit"]} | 多头损失: {self.obj["long_loss_profit"]} | 空头盈利: {self.obj["short_win_profit"]} | 空头损失: {self.obj["short_loss_profit"]} (本行统计含手续费)</br> ')
            file.write(f'多头净利润: {round(long_profit,2)} | 空头净利润: {round(short_profit,2)} | 总净利润: {round(long_profit+short_profit,2)} </br>')
            file.write(f'多头盈利因子: {long_factore} | 空头盈利因子: {short_factore} </br>')
            
            file.write(f'手续费: {round(self.obj["fee"],2)} </br>')

            file.write(f'盈利总次数: {self.obj["win_count"]} | 亏损总次数: {self.obj["loss_count"]} | 总胜率: {round(self.obj["win_rate"]*100,2)}% </br>')
            file.write(f'多头盈利次数: {self.obj["long_win_count"]} | 多头亏损次数: {self.obj["long_loss_count"]} | 多头胜率: {round(self.obj["long_win_rate"]*100,2)}% </br>')
            file.write(f'空头盈利次数: {self.obj["short_win_count"]} | 空头亏损次数: {self.obj["short_loss_count"]} | 空头胜率: {round(self.obj["short_win_rate"]*100,2)}% </br>')

            file.write(f'总平均持仓天数: {round(self.obj["total_avg_holding"],2)} | 多头平均持仓天数: {round(self.obj["long_avg_holding"],2)} | 空头平均持仓天数: {round(self.obj["short_avg_holding"],2)} ')
            file.write('</div>\n')

            file.write('<div id="container" style="height: 90%"></div>')
            file.write('<div id="container2" style="height: 50px"></div>')
            file.write('</body>\n')
            file.write('</html>')


    # 计算每天的手续费 
    def cal_daily_fee(self):
        daily_list = self.daily_df[self.daily_df['model_flag']==self.model_flag]
        daily_count = 0
        self.obj['fee'] =0
        
        for i,doc in daily_list.iterrows():
            daily_count+=1
            fee =0
            # 保证金
            long_fee =0
            short_fee =0
            # 计算手续费
            # st,et = bt_common.get_trading_day(doc['date'])
            equity_trade = self.order_df[(self.order_df['model_flag']==self.model_flag) & (self.order_df['trading_date']==doc['date'])]
            if len(equity_trade)>0 :
                for idx,item in equity_trade.iterrows():
                    _fee = (item['price']*item['count']*item['mul']*FEE_FEE)
                    fee += _fee
                    if item['buyOrSell'] == BUY:
                        long_fee += _fee
                    else:
                        short_fee += _fee
             # 统计所有的手续费
            self.obj['fee'] +=fee
            self.daily_df.loc[i,"fee"]=fee
            self.daily_df.loc[i,"long_fee"]=long_fee
            self.daily_df.loc[i,"short_fee"]=short_fee
    
    # 计算胜率相关
    def calc_winning(self):
        df = self.order_df[(self.order_df['model_flag']==self.model_flag) & (self.order_df['openOrClose']==CLOSE)]
        # 盈利 总次数
        self.obj['win_count'] = len(df[(df['price']-df['openPrice'])*df['buyOrSell']>0])
        # 亏损次数
        self.obj['loss_count'] = len(df[(df['price']-df['openPrice'])*df['buyOrSell']<=0])
        # 胜率
        self.obj['win_rate'] = self.obj['win_count'] / (self.obj['win_count']+self.obj['loss_count'])
        # 多头
        long_df = df[df['buyOrSell'] == BUY]
        self.obj['long_win_count'] = len(long_df[(long_df['price']-long_df['openPrice'])*long_df['buyOrSell']>0])
        self.obj['long_loss_count'] = len(long_df[(long_df['price']-long_df['openPrice'])*long_df['buyOrSell']<=0])
        if (self.obj['long_win_count']+self.obj['long_loss_count']) ==0:
            self.obj['long_win_rate'] =0
        else:
            self.obj['long_win_rate'] = self.obj['long_win_count'] / (self.obj['long_win_count']+self.obj['long_loss_count'])
        
        
        # 空头
        short_df = df[df['buyOrSell'] == SELL]
        self.obj['short_win_count'] = len(short_df[(short_df['price']-short_df['openPrice'])*short_df['buyOrSell']>0])
        self.obj['short_loss_count'] = len(short_df[(short_df['price']-short_df['openPrice'])*short_df['buyOrSell']<=0])
        if (self.obj['short_win_count']+self.obj['short_loss_count']) ==0:
            self.obj['short_win_rate']=0
        else:
            self.obj['short_win_rate'] = self.obj['short_win_count']/(self.obj['short_win_count']+self.obj['short_loss_count'])
        pass


    def calc_tp_lp(self):
        st = datetime.strptime(str(self.start_time), "%Y%m%d").strftime("%Y-%m-%d")
        et = datetime.strptime(str(self.end_time), "%Y%m%d").strftime("%Y-%m-%d")
        df = self.order_df[(self.order_df['trading_date']>=st) & (self.order_df['trading_date']<=et)]
        
        # 多头
        long_df = df[df['buyOrSell'] == BUY]
        # 多头盈利
        long_win_df = long_df[((long_df['price']-long_df['openPrice'])*long_df['buyOrSell'])>0]
        self.obj['long_win_profit'] = ((long_win_df['price']-long_win_df['openPrice'])*long_win_df['buyOrSell']*long_win_df['openOrClose']*long_win_df['count_back']*long_win_df['mul'] - long_win_df['fee']).sum()
        # 多头损失
        long_loss_df = long_df[((long_df['price']-long_df['openPrice'])*long_df['buyOrSell'])<=0]
        self.obj['long_loss_profit'] = ((long_loss_df['price']-long_loss_df['openPrice'])*long_loss_df['buyOrSell']*long_loss_df['openOrClose']*long_loss_df['count_back']*long_loss_df['mul'] - long_loss_df['fee']).sum()
        
        # 空头
        short_df = df[df['buyOrSell'] == SELL]
        # 空头盈利
        short_win_df =short_df[((short_df['price']-short_df['openPrice'])*short_df['buyOrSell'] )>0]
        self.obj['short_win_profit'] = ((short_win_df['price']-short_win_df['openPrice'])*short_win_df['buyOrSell']*short_win_df['openOrClose']*short_win_df['count_back']*short_win_df['mul'] - short_win_df['fee']).sum()
        # 空头损失
        short_loss_df = short_df[((short_df['price']-short_df['openPrice'])*short_df['buyOrSell']) <=0]
        self.obj['short_loss_profit'] = ((short_loss_df['price']-short_loss_df['openPrice'])*short_loss_df['buyOrSell']*short_loss_df['openOrClose']*short_loss_df['count_back']*short_loss_df['mul'] - short_loss_df['fee']).sum()

   

    # 添加持仓天数
    def add_holding_days(self):
        close_orders = self.order_df[(self.order_df["model_flag"]==self.model_flag) & (self.order_df["openOrClose"]==CLOSE)]
        for idx,doc in close_orders.iterrows():
            open_order = self.order_df[(self.order_df['tradeId'] == doc['ID'])&(self.order_df['openOrClose']==OPEN)].iloc[0]
            days = self.data_common.count_trading_days(open_order['datetime'],doc['datetime'])
            self.order_df.loc[idx,"holding_days"] = days

        

    # 1、对于每个持仓的交易，计算买入日期和卖出日期之间的天数差值（持仓天数）。
    # 2、将所有交易的持仓天数相加。
    # 3、将总持仓天数除以交易数量，得到平均持仓周期。
    def calc_holding(self):
        
        self.obj['long_holding']=0
        self.obj['short_holding']=0

        self.obj['long_holding'] = self.order_df[(self.order_df['buyOrSell']==BUY)&(self.order_df['openOrClose']==CLOSE)&(self.order_df['model_flag']==self.model_flag)]["holding_days"].sum()
       
        self.obj['short_holding'] = self.order_df[(self.order_df['buyOrSell']==SELL)&(self.order_df['openOrClose']==CLOSE)&(self.order_df['model_flag']==self.model_flag)]["holding_days"].sum()
        
        self.obj['total_holding'] = self.obj['long_holding']+self.obj['short_holding']

        self.obj['total_avg_holding'] = 0
        if self.obj['all_trade_count']>0:
            self.obj['total_avg_holding'] = self.obj['total_holding'] / self.obj['all_trade_count']

        self.obj['long_avg_holding']=0
        if self.obj['long_trade_count']>0:
            self.obj['long_avg_holding'] = self.obj['long_holding'] / self.obj['long_trade_count']

        self.obj['short_avg_holding']=0
        if self.obj['short_trade_count']>0:
            self.obj['short_avg_holding'] = self.obj['short_holding'] / self.obj['short_trade_count']




    def run(self):
       
        t = zutil.Calc_Time("insert_daily_equity")
        self.insert_daily_equity()
        t.t()
        t = zutil.Calc_Time("cal_daily_fee")
        self.cal_daily_fee()
        t.t()
        t = zutil.Calc_Time("calc_profit_float_and_all")
        self.calc_profit_float_and_all()
        t.t()
        t = zutil.Calc_Time("calc_profit_float_long_and_short")
        self.calc_profit_float_long_and_short()
        t.t()
        t = zutil.Calc_Time("profit")
        self.profit()
        t.t()
        t = zutil.Calc_Time("profit_factor")
        self.profit_factor()
        t.t()
        
        t = zutil.Calc_Time("sharpe_ratio")
        
        self.sharpe_ratio()
        t.t()
        t = zutil.Calc_Time("calc_max_drawdown")
        self.calc_max_drawdown()
        t.t()
        t = zutil.Calc_Time("calc_rate_ratio")
        self.calc_rate_ratio()
        t.t()
        t = zutil.Calc_Time("calc_winning")
        self.calc_winning()
        self.calc_tp_lp()
        t.t()
        t = zutil.Calc_Time("add_holding_days")
        self.add_holding_days()
        t.t()
        t = zutil.Calc_Time("calc_holding")
        self.calc_holding()
        t.t()
        t = zutil.Calc_Time("draw_plt")
        self.draw_plt()
        t.t()
       
        t = zutil.Calc_Time("json_2_file")
        self.json_2_file()
        t.t()
        self.daily_df.to_csv("./data/daily_df.csv")
        self.equity_order.to_csv('./data/equity_orders.csv')
