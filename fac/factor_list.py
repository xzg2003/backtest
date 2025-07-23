from .FCT_Bbiboll_Up import FCT_Bbiboll_Up
from .FCT_Ar_Vol_1 import FCT_Ar_Vol_1
from .FCT_Cr_Ref_1 import FCT_Cr_Ref_1
from .FCT_Bias_Vol_Dfive import FCT_Bias_Vol_Dfive
from .FCT_Vmacd import FCT_Vmacd
from .FCT_Avg_Amt_Big_Count_1 import FCT_Avg_Amt_Big_Count_1
from .FCT_Macd_1 import FCT_Macd_1
from .FCT_Br_Ref_1 import FCT_Br_Ref_1
from ..factor_cal.FCT_CHG import FCT_CHG
from .FCT_Mfi_Atr_Dfive import FCT_Mfi_Atr_Dfive
from .FCT_Atr_DFive_1 import FCT_Atr_DFive_1
from .FCT_Bbiboll_Down import FCT_Bbiboll_Down
from .FCT_Rsi_1 import FCT_Rsi_1

class Factor_list:

    def __init__(self):
        self.list={}

    def load_factors(self):
        f = FCT_Bbiboll_Up()
        self.list[f.factor_name] = f
        f = FCT_Ar_Vol_1()
        self.list[f.factor_name] = f
        f = FCT_Cr_Ref_1()
        self.list[f.factor_name] = f
        f = FCT_Bias_Vol_Dfive()
        self.list[f.factor_name] = f
        f = FCT_Vmacd()
        self.list[f.factor_name] = f
        f = FCT_Avg_Amt_Big_Count_1()
        self.list[f.factor_name] = f
        f = FCT_Macd_1()
        self.list[f.factor_name] = f
        f = FCT_Br_Ref_1()
        self.list[f.factor_name] = f
        f = FCT_CHG()
        self.list[f.factor_name] = f
        f = FCT_Mfi_Atr_Dfive()
        self.list[f.factor_name] = f
        f = FCT_Atr_DFive_1()
        self.list[f.factor_name] = f
        f = FCT_Bbiboll_Down()
        self.list[f.factor_name] = f
        f = FCT_Rsi_1()
        self.list[f.factor_name] = f
