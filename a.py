import ccxt
import decimal
import math
import pandas as pd
import csv

# 打開CSV文件
with open('your_file.csv', 'r', newline='') as csvfile:
    # 創建CSV讀取器
    csvreader = csv.reader(csvfile)
    
    # 迭代每一行
    for row in csvreader:
        # 在這裡你可以處理每一行的數據
        print(row)


def calculate_ema(data, window):
    return pd.Series([x[4] for x in data]).ewm(span=window, adjust=False).mean()

btc_ema = calculate_ema()