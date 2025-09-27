
import pandas as pd
import os
import math
import sys

sys.path.append(os.getcwd())

from config import FEE_FEE, AMOUNT_4_OPEN
import common.back_test_common as bt_common

BUY = 1
SELL = -1
OPEN = 0
CLOSE = 1


class Trade_Orders:
    def __init__(self, param: dict):
        # 兼容原参数，但这里只用时间过滤和路径参数
        self.t_st = param.get("st")
        self.t_et = param.get("et")
        self.position_path = param.get("position_path", "./data/position.csv")
        self.order_path = param.get("order_path", "./data/order.csv")

        self.model_flag = "pre_1"

        self.order_df = pd.DataFrame(
            columns=[
                "datetime",
                "order_date",
                "trading_date",
                "instrument_id",
                "instrument",
                "buyOrSell",
                "openOrClose",
                "price",
                "openPrice",
                "count",
                "count_back",
                "ID",
                "tradeId",
                "mul",
                "flag",
                "model_flag",
                "status",
                "fee",
            ]
        )

    # -------------------- I/O --------------------

    def load_position(self) -> pd.DataFrame:
        if not os.path.exists(self.position_path):
            raise FileNotFoundError(f"position.csv not found at {self.position_path}")

        # 处理 BOM、列名空格
        df = pd.read_csv(self.position_path, encoding="utf-8-sig")
        df.columns = df.columns.str.strip()

        required = ["datetime", "instrument", "open", "mul", "pos"]
        missing = [c for c in required if c not in df.columns]
        if missing:
            raise ValueError(
                f"position.csv 缺少必须字段 {missing}，至少需要 {required}"
            )

        # 兜底：缺 instrument_id / trading_date 时自动填充
        if "instrument_id" not in df.columns:
            df["instrument_id"] = df["instrument"]
        if "trading_date" not in df.columns:
            df["trading_date"] = df["datetime"]

        # 时间过滤（如果提供 st/et）
        if self.t_st:
            df = df[df["trading_date"] >= self.t_st]
        if self.t_et:
            df = df[df["trading_date"] <= self.t_et]

        # 排序：先品种再时间
        df = df.sort_values(by=["instrument", "datetime"]).reset_index(drop=True)
        return df

    def save_orders(self):
        # 保证目录存在
        # 如果目录已经存在，则在后面追加
        if not os.path.exists(self.order_path):
            self.order_df.to_csv(self.order_path, index=False)
            print(f"Order file saved to {self.order_path}")
        else:
            # 先打开原文件，再合并
            existing = pd.read_csv(self.order_path)
            self.order_df = pd.concat([existing, self.order_df], ignore_index=True)
            self.order_df.to_csv(self.order_path, index=False)

    # -------------------- 构造订单 --------------------

    def _build_open(self, row, direction: int):
        """direction: 1=开多, -1=开空"""
        price = float(row["open"])
        mul = float(row["mul"]) if pd.notna(row["mul"]) else 0.0
        if not (price > 0 and mul > 0):
            # 无法计算合约张数，跳过开仓
            return None, None

        count = math.floor(AMOUNT_4_OPEN / (price * mul))
        if count <= 0:
            # 资金不足以开1手，跳过
            return None, None

        trade_id = bt_common.generate_unique_string()
        order = {
            "datetime": row["datetime"],
            "order_date": row["datetime"],
            "trading_date": row["trading_date"],
            "instrument_id": row["instrument_id"],
            "instrument": row["instrument"],
            "buyOrSell": BUY if direction > 0 else SELL,  # 仓位方向
            "openOrClose": OPEN,
            "price": price,
            "openPrice": price,
            "count": count,
            "count_back": count,
            "ID": trade_id,
            "tradeId": trade_id,
            "mul": int(mul),
            "flag": 0,
            "model_flag": self.model_flag,
            "status": "open",
            "fee": count * price * mul * FEE_FEE,
        }
        # 记录开仓信息，供后续平仓使用
        opened = {
            "trade_id": trade_id,
            "direction": 1 if direction > 0 else -1,
            "open_price": price,
            "count": count,
            "mul": mul,
        }
        return order, opened

    def _build_close(self, row, opened: dict):
        """根据开仓信息生成对应的平仓单（方向保持为原仓位方向）"""
        price = float(row["open"])
        mul = float(opened["mul"])
        order = {
            "datetime": row["datetime"],
            "order_date": row["datetime"],
            "trading_date": row["trading_date"],
            "instrument_id": row["instrument_id"],
            "instrument": row["instrument"],
            "buyOrSell": BUY if opened["direction"] > 0 else SELL,  # 仍然是仓位方向
            "openOrClose": CLOSE,
            "price": price,
            "openPrice": opened["open_price"],
            "count": opened["count"],
            "count_back": opened["count"],
            "ID": opened["trade_id"],
            "tradeId": opened["trade_id"],
            "mul": int(mul),
            "flag": 0,
            "model_flag": self.model_flag,
            "status": "close",
            "fee": opened["count"] * price * mul * FEE_FEE,
        }
        return order

    # -------------------- 状态机核心 --------------------

    def convert_to_orders(self):
        df = self.load_position()

        for ins, g in df.groupby("instrument", sort=False):
            prev_pos = 0  # 上一时刻仓位方向
            opened = None  # 已开仓的挂钩信息（若存在）

            for _, row in g.iterrows():
                # 规范化信号到 {-1,0,1}
                raw = row["pos"]
                curr_pos = 0 if pd.isna(raw) else (1 if raw > 0 else (-1 if raw < 0 else 0))

                # 0 -> +1 / -1 ：直接开仓
                if prev_pos == 0 and curr_pos != 0:
                    open_order, opened = self._build_open(row, curr_pos)
                    if open_order:
                        self.order_df.loc[len(self.order_df)] = open_order
                        prev_pos = curr_pos
                    else:
                        # 开仓失败（资金不足/价格无效），保持空仓状态
                        prev_pos = 0
                        opened = None
                    continue

                # +1（持多）
                if prev_pos == 1:
                    if curr_pos == 1:
                        # 持有不变
                        continue
                    # 平多
                    if opened:
                        close_order = self._build_close(row, opened)
                        self.order_df.loc[len(self.order_df)] = close_order
                        opened = None

                    if curr_pos == 0:
                        prev_pos = 0
                        continue
                    if curr_pos == -1:
                        # 平多后开空
                        open_order, opened = self._build_open(row, -1)
                        if open_order:
                            self.order_df.loc[len(self.order_df)] = open_order
                            prev_pos = -1
                        else:
                            prev_pos = 0
                            opened = None
                        continue

                # -1（持空）
                if prev_pos == -1:
                    if curr_pos == -1:
                        # 持有不变
                        continue
                    # 平空
                    if opened:
                        close_order = self._build_close(row, opened)
                        self.order_df.loc[len(self.order_df)] = close_order
                        opened = None

                    if curr_pos == 0:
                        prev_pos = 0
                        continue
                    if curr_pos == 1:
                        # 平空后开多
                        open_order, opened = self._build_open(row, 1)
                        if open_order:
                            self.order_df.loc[len(self.order_df)] = open_order
                            prev_pos = 1
                        else:
                            prev_pos = 0
                            opened = None
                        continue

            # 该品种到最后还有未平仓 -> 在最后一条记录处强制平仓
            if prev_pos != 0 and opened is not None and len(g) > 0:
                last_row = g.iloc[-1]
                close_order = self._build_close(last_row, opened)
                self.order_df.loc[len(self.order_df)] = close_order

    # -------------------- 入口 --------------------

    def main(self):
        self.convert_to_orders()
        self.save_orders()
