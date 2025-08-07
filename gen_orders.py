
import pandas as pd
import os
import math
import sys

sys.path.append(os.getcwd())

from config import FEE_FEE, AMOUNT_4_OPEN
import common.util as zutil
import common.back_test_common as bt_common

BUY = 1
SELL = -1
OPEN = 0
CLOSE = 1

class PositionToOrderConverter:
    def __init__(self, position_path="./data/position.csv", order_path="./data/order.csv"):
        self.position_path = './data/position.csv' 
        self.order_path = order_path
        self.model_flag = "pre_1"
        self.order_df = pd.DataFrame(columns=[
            'datetime', 'order_date', 'trading_date', 'instrument_id', 'instrument',
            'buyOrSell', 'openOrClose', 'price', 'openPrice', 'count', 'count_back',
            'ID', 'tradeId', 'mul', 'flag', 'model_flag', 'status', 'fee'
        ])

    def load_position(self):
        if not os.path.exists(self.position_path):
            raise FileNotFoundError(f"position.csv not found at {self.position_path}")
        return pd.read_csv(self.position_path)

    def convert_to_orders(self):
        df = self.load_position()
        df = df.sort_values(by='datetime')

        # 遍历每行持仓信号，生成开/平仓订单
        for idx, row in df.iterrows():
            signal = row['pos']  # 1=多头开仓，-1=空头开仓，0=平仓

            if signal == 0:
                continue

            open_order = self.build_order(row, signal, OPEN)
            self.order_df.loc[len(self.order_df)] = open_order

            # 生成配套平仓单，简单起见我们模拟为下一个周期平仓
            close_order = self.build_order(row, signal, CLOSE)
            close_order['openPrice'] = open_order['price']
            close_order['ID'] = open_order['tradeId']
            close_order['tradeId'] = open_order['tradeId']
            close_order['status'] = 'close'

            self.order_df.loc[len(self.order_df)] = close_order

    def build_order(self, row, signal, openOrClose):
        price = row['open']
        trade_id = bt_common.generate_unique_string()
        count = math.floor(AMOUNT_4_OPEN / (price * row['mul']))

        order = {
            'datetime': row['datetime'],
            'order_date': row['datetime'],
            'trading_date': row['trading_date'],
            'instrument_id': row['instrument_id'],
            'instrument': row['instrument'],
            'buyOrSell': BUY if signal > 0 else SELL,
            'openOrClose': openOrClose,
            'price': price,
            'openPrice': price,
            'count': count,
            'count_back': count,
            'ID': trade_id,
            'tradeId': trade_id,
            'mul': int(row['mul']),
            'flag': 0,
            'model_flag': self.model_flag,
            'status': 'open' if openOrClose == OPEN else 'close',
            'fee': count * price * row['mul'] * FEE_FEE
        }
        return order

    def run(self):
        self.convert_to_orders()
        self.order_df.to_csv(self.order_path, index=False)
        print(f"Order file saved to {self.order_path}")

