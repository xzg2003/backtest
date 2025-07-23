# 根据模型名称导入模型
import importlib
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
from config import model_name

module = importlib.import_module(model_name)
MODEL = getattr(module, "MODEL")  