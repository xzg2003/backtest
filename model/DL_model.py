import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import time
import common.util as zutil
import pandas as pd
# 定义模型
class ConvNet(nn.Module):
    def __init__(self, dim):
        super(ConvNet, self).__init__()
        self.conv1 = nn.Conv1d(in_channels=1, out_channels=16, kernel_size=3, padding=1)
        self.relu1 = nn.ReLU()
        self.pool1 = nn.MaxPool1d(kernel_size=2)

        self.conv2 = nn.Conv1d(in_channels=16, out_channels=32, kernel_size=3, padding=1)
        self.relu2 = nn.ReLU()
        self.pool2 = nn.MaxPool1d(kernel_size=2)

        self.flatten = nn.Flatten()
        self.fc1 = nn.Linear(32*(dim//4), 1) 
        #self.output = nn.Sigmoid()
        #self.relu3 = nn.ReLU()
        #self.fc2 = nn.Linear(64, 1)

    def forward(self, x):
        x = self.conv1(x)      # (N, 16, dim)
        x = self.relu1(x)
        x = self.pool1(x)      # (N, 16, dim/2)

        x = self.conv2(x)      # (N, 32, dim/2)
        x = self.relu2(x)
        x = self.pool2(x)      # (N, 32, dim/4)

        x = self.flatten(x)    # (N, 32*dim/4)
        x = self.fc1(x)        # (N, 1)
        #x= self.output(x)
        return x

class model():
    def __init__(self, instuments, x_train, y_train, x_test, x_pre_test, param={}):
        if 'epochs' in param.keys():
            epochs = param['epochs']
        else:
            epochs = 50
        self.epochs = epochs
        self.model = ConvNet(x_train.shape[1])
        self.best_model = self.model
        self.x_train = x_train # 训练集的特征
        self.y_train = y_train # 训练集的标签
        self.x_test = x_test # 测试集的特征
        self.x_pre_test = x_pre_test # 存放市场数据与模型预测结果合并后的表格
        self.instuments = instuments

    def prepare_train_data(self):
        x = self.x_train.to_numpy().astype(np.float32)
        y = self.y_train.to_numpy().astype(np.float32)
        self.x_train = torch.from_numpy(x).unsqueeze(1)   
        self.y_train = torch.from_numpy(y)
    
    def train(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f'Using device: {self.device}')
        self.model.to(self.device)
        optimizer = optim.Adam(self.model.parameters(), lr=0.001)
        criterion = nn.MSELoss()
        x = self.x_train.to(self.device)       
        y = self.y_train.to(self.device)
        min_loss=1e+6
        for epoch in range(self.epochs):
            start = time.time()
            self.model.train()
            optimizer.zero_grad()
            outputs = self.model(x)            # 前向传播
            loss = criterion(outputs, y)  # 计算损失
            loss.backward()                      # 反向传播
            optimizer.step()                     # 更新参数
            end = time.time()
            print(f'Epoch [{epoch+1}/{self.epochs}], Loss: {loss.item():.4f}, Time:{(end-start):.4f}s')
            if loss.item()<min_loss:
                min_loss = loss.item()
                torch.save(self.model.state_dict(), f'./model/DL_model/model.pkl')
                self.best_model = self.model
                print('模型已保存')
        print('训练完成')
    
    def test(self):
        self.best_model.eval()
        self.result = []
        for instrument in self.instuments:
            x = self.x_test[self.x_test['instrument'] == instrument].copy()
            df = self.x_pre_test[self.x_pre_test['instrument'] == instrument].copy()
            x = x.to_numpy().astype(np.float32)
            x = torch.from_numpy(x).unsqueeze(1).to(self.device)
            #print(x)
            with torch.no_grad():
                outputs = self.best_model(x).to('cpu')
                pre = pd.DataFrame(outputs.numpy(),columns=['pre'])
                df['pre'] = pre.shift(1)   
                self.result.append(df)
            
        self.result = pd.concat(self.result, axis=0, ignore_index=True)
        zutil.save_file(self.result,f'./data/pre.csv')
    
    def run(self):
        self.prepare_train_data()
        self.train()
        self.test()