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
    return data['close'].ewm(span=window, adjust=False).mean()


def calculate_rolling_returns(data, window):
    """
    計算滾動回報率
    """
    return data['close'].pct_change(window)

exchange = ccxt.okx()

btc_data = read_csv('SOL_BTC')

print(btc_data)
btc_rolling_returns = calculate_rolling_returns(btc_data,3)
print(btc_rolling_returns)
btc_signal = btc_rolling_returns.iloc[-1]
print(btc_signal)
import ccxt

# 初始化交易所
exchange = ccxt.okx({
    'apiKey': '0de1ec2d-9261-4915-9104-519294dd9c7e',
    'secret': 'F58CBB3F57E902C0FF702C33F05008C0',
    'password': '!Aa5566288'
})

# 加载市场信息
markets = exchange.load_markets()
symbol = 'BTC/USDT'

# 获取账户余额
balance = exchange.fetch_balance()
usdt_balance = balance['total']['USDT']

# 获取交易对信息
market = exchange.market(symbol)

# 确定可用于购买 BTC 的最大 USDT 金额
# 这里考虑到交易所可能有最大订单金额的限制
max_order_value = min(usdt_balance, market['limits']['amount']['max'] * market['info']['last'])

print(f"您可以使用最多 {max_order_value} USDT 来购买 BTC。")

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