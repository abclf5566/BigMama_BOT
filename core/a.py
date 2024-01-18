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

exchange = ccxt.okx({
    'apiKey': '0de1ec2d-9261-4915-9104-519294dd9c7e',
    'secret': 'F58CBB3F57E902C0FF702C33F05008C0',
    'password': '!Aa5566288'
})

btc_data = read_csv('SOL_BTC')

print(btc_data)
btc_rolling_returns = calculate_rolling_returns(btc_data,3)
print(btc_rolling_returns)
btc_signal = btc_rolling_returns.iloc[-1]
print(btc_signal)

def evaluate_current_position():
    # 獲取市場價格
    btc_price = exchange.fetch_ticker('BTC/USDT')['last']
    symbol_2_price = exchange.fetch_ticker('SOL/USDT')['last']

    # 獲取賬戶余額
    balance = exchange.fetch_balance()
    print(balance)

    # 計算各資產的價值（以USDT為單位）
    btc_balance = balance['BTC'].get('free', 0)
    symbol_2_balance = balance.get('SOL', {}).get('free', 0)
    usdt_balance = balance['USDT'].get('free', 0)
    usdt_value = balance['USDT']['free']

    btc_value = btc_balance * btc_price
    symbol_2_value = symbol_2_balance * symbol_2_price
    usdt_value = usdt_balance
    
    # 比較各資產價值，選擇最大的作為當前持倉
    if btc_value > symbol_2_value and btc_value > usdt_value:
        return 'BTC'
    elif symbol_2_value > btc_value and symbol_2_value > usdt_value:
        return 'SOL'
    else:
        return 'USDT'

eav = evaluate_current_position()
print(eav)

def evaluate_current_position(self):
    # 获取市场价格
    btc_price = self.exchange.fetch_ticker('BTC/USDT')['last']
    symbol_2_price = self.exchange.fetch_ticker(f'{self.symbol_2}/USDT')['last']

    # 获取账户余额
    balance = self.exchange.fetch_balance()

    # 安全地获取各资产的余额（如果没有则返回0）
    btc_balance = balance['BTC'].get('free', 0)
    symbol_2_balance = balance.get(self.symbol_2, {}).get('free', 0)
    usdt_balance = balance['USDT'].get('free', 0)

    # 计算各资产的价值（以USDT为单位）
    btc_value = btc_balance * btc_price
    symbol_2_value = symbol_2_balance * symbol_2_price
    usdt_value = usdt_balance

    # 比较各资产价值，选择最大的作为当前持仓
    if btc_value > symbol_2_value and btc_value > usdt_value:
        return 'BTC'
    elif symbol_2_value > btc_value and symbol_2_value > usdt_value:
        return self.symbol_2
    else:
        return 'USDT'
    

def calculate_trade_decision(current_position,symbol_2, btc_signal, symbol_2_signal, symbol_2_btc_signal, az, signal_threshold):
    """
    根據BTC、symbol_2和symbol_2/BTC的信號確定交易決策。
    :param current_position: 當前持倉 ('BTC', 'symbol_2', 'USDT')。
    :param btc_signal: BTC的信號。
    :param symbol_2_signal: symbol_2的信號。
    :param symbol_2_btc_signal: symbol_2/BTC交易對的信號。
    :param az: 中性區間的閾值。
    :param signal_threshold: 信號閾值。
    :return: 新的持倉位置（'BTC'、'symbol_2'或'USDT'）。
    """

    # 當前最佳收益 中性區間判斷，如果在az中性區內且兩幣種相對於USDT都下跌，則優先處理轉換為USDT
    if -az <= btc_signal <= az and -az <= symbol_2_signal <= az:
        if current_position == 'BTC' and symbol_2_btc_signal > 0:
            return f'{symbol_2}'
        elif current_position == f'{symbol_2}' and symbol_2_btc_signal < 0:
            return 'BTC'
        else:
            return current_position

    # 如果BTC和symbol_2相對於USDT的信號都小於0，則轉換為USDT
    elif btc_signal < 0 and symbol_2_signal < 0:
        return 'USDT'
    else:
        # 根據symbol_2/BTC信號進行持倉決策
        if current_position == 'BTC' and symbol_2_btc_signal > 0:
            return f'{symbol_2}'
        elif current_position == f'{symbol_2}' and symbol_2_btc_signal < 0:
            return 'BTC'
        else:
            # 根據BTC和symbol_2相對於USDT的信號差異進行決策
            if abs(btc_signal - symbol_2_signal) > signal_threshold:

                return 'BTC' if btc_signal > symbol_2_signal else f'{symbol_2}'
            else:
                return current_position
current_position = 'USDT'
symbol_2 = 'SOL'
KlineNum = 9
KlineNum2 = 16
az = 0.06
signal_threshold = 0.08
ema = 39
ema_2 = 179

new_position = calculate_trade_decision(current_position, symbol_2, btc_signal, symbol_2_signal, symbol_2_btc_signal, az, signal_threshold)
print(new_position)



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