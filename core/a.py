import ccxt
import decimal
import math
import pandas as pd
import csv
import os

# 設定目錄路徑
directory_path = './dailydata/'

# 使用os模組的listdir()函數列出目錄下的所有文件名稱
csv_file = os.listdir(directory_path)
print(csv_file)

# 迭代並打印每個文件名稱
for file_name in csv_file:
    print(file_name)

# # 打開CSV文件
# with open('dailydata/', 'r', newline='') as csvfile:
#     # 創建CSV讀取器
#     csvreader = csv.reader(csvfile)
    
#     # 迭代每一行
#     for row in csvreader:
#         # 在這裡你可以處理每一行的數據
#         print(row)



def read_csv(filename):
    try:
        # 使用pandas的read_csv函數來讀取CSV文件
        df = pd.read_csv(f'dailydata/{filename}.csv')
        return df
    except FileNotFoundError:
        print(f"{filename}.csv 文件不存在.")
        return None
def calculate_ema(data, window):
    return pd.Series([x[4] for x in data]).ewm(span=window, adjust=False).mean()
# def calculate_ema(data, window):
#     # 假設 data DataFrame 有一個名為 'close' 的列代表收盤價
#     return data['close'].ewm(span=window, adjust=False).mean()

# def calculate_rolling_returns(data, window):
#     """
#     計算滾動回報率
#     """
#     return data['close'].pct_change(window)

def calculate_rolling_returns(data, window):
    """
    計算滾動回報率
    """
    return pd.Series([x[4] for x in data]).pct_change(window)

exchange = ccxt.okx()

btc_data = exchange.fetch_ohlcv('BTC/USDT')
# print(calculate_ema(btc_data, 30))
# rolling_returns = calculate_ema(btc_data, 30)
# calculate_rolling_returns_1 = calculate_rolling_returns(rolling_returns,20)
# btc_signal = calculate_rolling_returns_1.iloc[-2]

btc_rolling_returns = calculate_rolling_returns(btc_data,20)
print(btc_rolling_returns)
btc_signal = btc_rolling_returns.iloc[-2]
print(btc_signal)

# 讀取CSV文件並計算EMA
#btc_data = read_csv("BTC_USDT")
# if btc_data is not None:
#     print("read calculate_ema")
#     ema = calculate_ema(btc_data, 40)
#     print(f'EMA is {ema} ')
#     print(calculate_rolling_returns(ema,5))


# def fetch_ohlcv(self, symbol, timeframe='1d', since=None, max_retries=5, sleep_interval=5):
#     retries = 0
#     while retries < max_retries:
#         try:
#             ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, since)
#             return ohlcv
#         except (ccxt.NetworkError, ccxt.ExchangeError) as e:
#             print(f"獲取數據時發生錯誤：{e}. 正在重試...")
#             retries += 1
#             time.sleep(sleep_interval)
#     raise Exception("獲取OHLCV數據失敗，達到最大重試次數。")

# btc_data = file_names
# symbol_2_data = fetch_ohlcv(f'{symbol_2}/USDT')
# symbol_2_btc_data = fetch_ohlcv(f'{symbol_2}/BTC')

# btc_rolling_returns = calculate_rolling_returns(btc_data, KlineNum)
# symbol_2_rolling_returns = calculate_rolling_returns(symbol_2_data, KlineNum)
# symbol_2_btc_rolling_returns = calculate_rolling_returns(symbol_2_btc_data, KlineNum2)

# btc_signal = btc_rolling_returns.iloc[-2]
# symbol_2_signal = symbol_2_rolling_returns.iloc[-2]
# symbol_2_btc_signal = symbol_2_btc_rolling_returns.iloc[-2]