
import ccxt
import pandas as pd
import time
import decimal
import math
from datetime import datetime


def count_decimal_places(value):
    # 將數值轉換為 Decimal 以避免浮點數的不精確性
    value_decimal = decimal.Decimal(str(value))
    # 取得小數部分
    decimal_part = value_decimal.as_tuple().exponent
    # 計算小數位數，如果沒有小數則為0
    return abs(decimal_part) if decimal_part < 0 else 0

def truncate(number, digits) -> float:
    """
    無條件捨去
    """
    stepper = 10.0 ** digits
    return math.floor(stepper * number) / stepper

class TradingBot:
    def __init__(self, symbol_2, api_key, secret, password, KlineNum = 10, KlineNum2 = 8, az = 0.08, signal_threshold = 0.09, ema=100, ema_2=100):
        self.exchange = ccxt.okx({
            'apiKey': api_key,
            'secret': secret,
            'password': password
        })
        self.symbol_2 = symbol_2
        self.KlineNum = KlineNum
        self.KlineNum2 = KlineNum2
        self.az = az
        self.signal_threshold = signal_threshold
        self.ema = ema
        self.ema_2 = ema_2

    def calculate_ema(self, data, window):
        return pd.Series([x[4] for x in data]).ewm(span=window, adjust=False).mean()

    def fetch_ohlcv(self, symbol, timeframe='1d', since=None, max_retries=5, sleep_interval=5):
        retries = 0
        while retries < max_retries:
            try:
                ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, since)
                return ohlcv
            except (ccxt.NetworkError, ccxt.ExchangeError) as e:
                print(f"獲取數據時發生錯誤：{e}. 正在重試...")
                retries += 1
                time.sleep(sleep_interval)
        raise Exception("獲取OHLCV數據失敗，達到最大重試次數。")

    def calculate_rolling_returns(self, data, window):
        """
        計算滾動回報率
        """
        return pd.Series([x[4] for x in data]).pct_change(window)


    def execute_trade_with_fallback(self, symbol, amount, target_position):
        """
        嘗試執行交易，如果出現錯誤則記錄下單嘗試
        """

        try:
            # 下市價買單，使用 `quoteOrderQty`
            params = {
                'quoteOrderQty': amount*0.999  # 指定想要花費的數量
            }

            # 獲取交易對的當前市場價格
            market_price = self.exchange.fetch_ticker(f'{symbol}')['last']

            # 計算最大可購買的目標交易數量
            #amount = amount / market_price

            if symbol in ['BTC/USDT', f'{symbol_2}/USDT'] and target_position == 'USDT':
                # 執行賣出操作
                print(f'使用 {symbol.split("/")[0]} 賣出換取USDT')
                order_info = self.exchange.create_market_sell_order(symbol, amount)

            elif symbol == f'{symbol_2}/BTC':
                if target_position == f'{symbol_2}':
                    # 從BTC轉換到AVAX，執行買入操作
                    print(f'使用BTC購買{symbol_2}')
                    order_info = self.exchange.create_market_buy_order(symbol, amount)
                    client_order_id = order_info['clientOrderId']
                    print("訂單 ID:", client_order_id)
                
                else:
                    # 從AVAX轉換到BTC，執行賣出操作
                    print(f'使用{symbol_2}賣出換取BTC')
                    order_info = self.exchange.create_market_sell_order(symbol, amount)
                    client_order_id = order_info['clientOrderId']
                    print("訂單 ID:", client_order_id)

            elif symbol == 'BTC/USDT' and target_position == 'BTC':
                # 使用USDT購買BTC
                print(f'使用 {amount} USDT購買BTC')
                order_info = self.exchange.create_market_buy_order(symbol, amount)
                client_order_id = order_info['clientOrderId']
                print("訂單 ID:", client_order_id)

            elif symbol == f'{symbol_2}/USDT' and target_position == f'{symbol_2}':
                # 使用USDT購買AVAX
                print(f'使用 {amount} USDT購買{symbol_2}')
                order_info = self.exchange.create_market_buy_order(symbol, amount)
                client_order_id = order_info['clientOrderId']
                print("訂單 ID:", client_order_id)

            else:
                # 對於其他交易對，按照原來的邏輯執行
                if target_position == 'USDT':
                    self.exchange.create_market_sell_order(symbol, None,params)
            print(f"成功下單: {symbol} 數量 {amount}")
        except ccxt.InvalidOrder as e:
            print(f"下單失敗，訂單不合法: {e}. 交易嘗試: {symbol} 數量 {amount}")
        except ccxt.InsufficientFunds as e:
            print(f"下單失敗，余額不足: {e}. 交易嘗試: {symbol} 數量 {amount}")
        except Exception as e:
            print(f"下單失敗，出現其他錯誤: {e}. 交易嘗試: {symbol} 數量 {amount}")

    def evaluate_positions_and_trade(self):
        """
        評估持倉並執行交易邏輯
        """
        btc_data = self.fetch_ohlcv('BTC/USDT')
        symbol_2_data = self.fetch_ohlcv(f'{symbol_2}/USDT')
        symbol_2_btc_data = self.fetch_ohlcv(f'{symbol_2}/BTC')

        btc_rolling_returns = self.calculate_rolling_returns(btc_data, self.KlineNum)
        symbol_2_rolling_returns = self.calculate_rolling_returns(symbol_2_data, self.KlineNum)
        symbol_2_btc_rolling_returns = self.calculate_rolling_returns(symbol_2_btc_data, self.KlineNum2)

        btc_signal = btc_rolling_returns.iloc[-2]
        symbol_2_signal = symbol_2_rolling_returns.iloc[-2]
        symbol_2_btc_signal = symbol_2_btc_rolling_returns.iloc[-2]

        market_info = self.exchange.load_markets()
        symbol_info = market_info['BTC/USDT']
        symbol_2_info = market_info[f'{symbol_2}/USDT']
        amount_value = count_decimal_places(symbol_info['precision']['amount'])
        amount_value_2 = count_decimal_places(symbol_2_info['precision']['amount'])

        balance = self.exchange.fetch_balance()

        balance_amount = balance['free'].get('BTC', 0)
        btc_balance = truncate(balance_amount, amount_value)

        balance_amount_2 = balance['free'].get(f'{symbol_2}', 0)
        symbol_2_balance = truncate(balance_amount_2, amount_value_2)

        balance_amount_usdt = balance['free'].get('USDT', 0)
        usdt_balance = truncate(balance_amount_usdt, 2)

        btc_ema = self.calculate_ema(btc_data, self.ema)
        symbol_2_ema = self.calculate_ema(symbol_2_data, self.ema_2)

        btc_price = btc_data[-1][4]  # 最新的BTC收盤價
        symbol_2_price = symbol_2_data[-1][4]  # 最新的AVAX收盤價

        current_position = 'USDT'  # 假設初始持倉為USDT

        if 'BTC' in balance['total']:
            if balance['BTC']['free'] > 0.0001:  # 設定一個最小BTC餘額閾值
                current_position = 'BTC'
        elif f'{symbol_2}' in balance['total']:
            if balance[f'{symbol_2}']['free'] > 0.01:  # 設定一個最小AVAX餘額閾值
                current_position = f'{symbol_2}'
        
                
        # 檢查價格是否跌破EMA100
        if btc_price < btc_ema.iloc[-1] or symbol_2_price < symbol_2_ema.iloc[-1]:
            print("價格跌破EMA100，轉換至USDT")
            self.execute_trade_with_fallback('BTC/USDT', btc_balance, 'USDT')
            self.execute_trade_with_fallback(f'{symbol_2}/USDT', symbol_2_balance, 'USDT')
            target_position = 'USDT'

        # 決策邏輯
        if -self.az <= btc_signal <= self.az and -self.az <= symbol_2_signal <= self.az:
            if btc_signal < 0 and symbol_2_signal < 0:
                print(f"信號在中性區且BTC/{symbol_2}信號小於0保持當前持倉")
                target_position = current_position

            elif current_position == 'BTC' and symbol_2_btc_signal > 0:
                print(f"信號在中性區BTC轉換至{symbol_2}")
                self.execute_trade_with_fallback(f'{symbol_2}/BTC', btc_balance, f'{symbol_2}')
                self.execute_trade_with_fallback(f'{symbol_2}/USDT', usdt_balance, f'{symbol_2}')
                target_position = f'{symbol_2}'

            elif current_position == f'{symbol_2}' and symbol_2_btc_signal < 0:
                print(f"信號在中性區{symbol_2}轉換至BTC")
                self.execute_trade_with_fallback(f'{symbol_2}/BTC', symbol_2_balance, 'BTC')
                self.execute_trade_with_fallback('BTC/USDT', usdt_balance, 'BTC')
                target_position = 'BTC'

            else:
                print("信號在中性區信號保持當前持倉")
                target_position = current_position

        elif btc_signal < 0 and symbol_2_signal < 0:
            print(f"{symbol_2}/BTC訊號為負轉換至USDT")
            self.execute_trade_with_fallback('BTC/USDT', btc_balance, 'USDT')
            self.execute_trade_with_fallback(f'{symbol_2}/USDT', symbol_2_balance, 'USDT')
            target_position = 'USDT'

        else:
            if current_position == 'BTC' and symbol_2_btc_signal > 0:
                print(f"轉換至{symbol_2}")
                self.execute_trade_with_fallback(f'{symbol_2}/BTC', btc_balance, f'{symbol_2}')
                self.execute_trade_with_fallback(f'{symbol_2}/USDT', usdt_balance, f'{symbol_2}')
                target_position = f'{symbol_2}'

            elif current_position == f'{symbol_2}' and symbol_2_btc_signal < 0:
                print("轉換至BTC")
                self.execute_trade_with_fallback(f'{symbol_2}/BTC', symbol_2_balance, 'BTC')
                self.execute_trade_with_fallback('BTC/USDT', usdt_balance, 'BTC')            
                target_position = 'BTC'
            else:
                if abs(btc_signal - symbol_2_signal) > self.signal_threshold:
                    if btc_signal > symbol_2_signal:
                        print("signal_threshold轉換至BTC")
                        self.execute_trade_with_fallback(f'{symbol_2}/BTC', symbol_2_balance, 'BTC')
                        self.execute_trade_with_fallback('BTC/USDT', usdt_balance, 'BTC')    
                        target_position = 'BTC'
                    else :
                        print(f"signal_threshold轉換至{symbol_2}")
                        self.execute_trade_with_fallback(f'{symbol_2}/BTC', btc_balance, f'{symbol_2}')
                        self.execute_trade_with_fallback(f'{symbol_2}/USDT', usdt_balance, f'{symbol_2}')                    
                        target_position = f'symbol_2'
                else:
                    target_position = current_position


        print(f"BTC滾動回報率: {btc_signal*100:.3f}%, {symbol_2}滾動回報率: {symbol_2_signal*100:.3f}%, {symbol_2}/BTC滾動回報率: {symbol_2_btc_signal*100:.3f}%")
        print(f"當前BTC價格{btc_price} BTC100EMA {btc_ema.iloc[-1]}")
        print(f"當前{symbol_2}價格{symbol_2_price} {symbol_2} 100EMA {symbol_2_ema.iloc[-1]}")    
        print(f"當前持倉: {current_position}, 目標持倉: {target_position}")

    def run(self):
        first_run = True  # 添加一個標誌來標示第一次運行

        while True:
            current_time = datetime.now()

            # 在第一次運行時立即執行交易邏輯
            if first_run:
                self.evaluate_positions_and_trade()
                print(f"首次執行交易邏輯於 {current_time}")
                first_run = False  # 更新標誌以避免重複運行

            # 每小時執行一次交易邏輯
            if current_time.minute == 1 and current_time.second == 0:
                self.evaluate_positions_and_trade()
                print(f"已於{current_time}執行交易邏輯")
                time.sleep(60)

            time.sleep(1)



#79EMA 169EMA 最佳参数组合: (20, 37, 0.1, 0.03) 最大回撤: 56.04% 最大回撤發生的時間段: 從 2021-05-18 00:00:00 到 2021-05-23 00:00:00 年化收益: 444.42% 最終資產價值: 308451.71 USDT 勝率為50.47% 1d btc/matic/usdt
#BTC 39EMA SOL 179EMA  最佳参数组合: (9, 16, 0.06, 0.08)  最大回撤: 37.75% 最大回撤發生的時間段: 從 2021-05-18 00:00:00 到 2021-06-01 00:00:00 年化收益: 575.71% 最終資產價值: 614620.49 USDT 勝率為49.26% 1d btc/SOL/usdt
            
# 使用示例
api_key = '0de1ec2d-9261-4915-9104-519294dd9c7e'
secret = 'F58CBB3F57E902C0FF702C33F05008C0'
password = '!Aa5566288'
symbol_2 = 'SOL'
KlineNum = 9
KlineNum2 = 16
az = 0.06
signal_threshold = 0.08
ema = 39
ema_2 = 179
bot = TradingBot(symbol_2, api_key, secret, password, ema=ema, ema_2=ema_2, KlineNum=KlineNum, KlineNum2=KlineNum2, az=az, signal_threshold=signal_threshold)
bot.run()