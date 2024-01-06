from discord.ext import commands
import ccxt
import pandas as pd
import time
from datetime import datetime


class Cog_extension(commands.Cog):
    def __int__(self,bot):
        self.bot=bot

import ccxt
import pandas as pd
import time
from datetime import datetime
class TradingBot:
    def __init__(self, api_key, secret, password, KlineNum = 10, KlineNum2 = 8, az = 0.08, signal_threshold = 0.09):
        self.exchange = ccxt.okx({
            'apiKey': api_key,
            'secret': secret,
            'password': password
        })
        self.KlineNum = KlineNum
        self.KlineNum2 = KlineNum2
        self.az = az
        self.signal_threshold = signal_threshold

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
            amount = amount / market_price

            if symbol in ['BTC/USDT', 'AVAX/USDT'] and target_position == 'USDT':
                # 執行賣出操作
                print(f'使用 {symbol.split("/")[0]} 賣出換取USDT')
                order_info = self.exchange.create_market_sell_order(symbol, amount)

            elif symbol == 'AVAX/BTC':
                if target_position == 'AVAX':
                    # 從BTC轉換到AVAX，執行買入操作
                    print('使用BTC購買AVAX')
                    order_info = self.exchange.create_market_buy_order(symbol, amount)
                    client_order_id = order_info['clientOrderId']
                    print("訂單 ID:", client_order_id)
                
                else:
                    # 從AVAX轉換到BTC，執行賣出操作
                    print('使用AVAX賣出換取BTC')
                    order_info = self.exchange.create_market_sell_order(symbol, amount)
                    client_order_id = order_info['clientOrderId']
                    print("訂單 ID:", client_order_id)

            elif symbol == 'BTC/USDT' and target_position == 'BTC':
                # 使用USDT購買BTC
                print(f'使用 {amount} USDT購買BTC')
                order_info = self.exchange.create_market_buy_order(symbol, amount)
                client_order_id = order_info['clientOrderId']
                print("訂單 ID:", client_order_id)

            elif symbol == 'AVAX/USDT' and target_position == 'AVAX':
                # 使用USDT購買AVAX
                print(f'使用 {amount} USDT購買AVAX')
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
        AVAX_data = self.fetch_ohlcv('AVAX/USDT')
        AVAX_btc_data = self.fetch_ohlcv('AVAX/BTC')

        btc_rolling_returns = self.calculate_rolling_returns(btc_data, self.KlineNum)
        AVAX_rolling_returns = self.calculate_rolling_returns(AVAX_data, self.KlineNum)
        AVAX_btc_rolling_returns = self.calculate_rolling_returns(AVAX_btc_data, self.KlineNum2)

        btc_signal = btc_rolling_returns.iloc[-2]
        AVAX_signal = AVAX_rolling_returns.iloc[-2]
        AVAX_btc_signal = AVAX_btc_rolling_returns.iloc[-2]

        balance = self.exchange.fetch_balance()
        btc_balance = round(balance['free'].get('BTC', 0), 9)
        AVAX_balance = round(balance['free'].get('AVAX', 0), 5)
        usdt_balance = round(balance['free'].get('USDT', 0), 2)

        btc_ema100 = self.calculate_ema(btc_data, 100)
        AVAX_ema100 = self.calculate_ema(AVAX_data, 100)

        btc_price = btc_data[-1][4]  # 最新的BTC收盘价
        AVAX_price = AVAX_data[-1][4]  # 最新的AVAX收盘价

        current_position = 'USDT'  # 假設初始持倉為USDT

        if 'BTC' in balance['total']:
            if balance['BTC']['free'] > 0.0001:  # 設定一個最小BTC餘額閾值
                current_position = 'BTC'
        elif 'AVAX' in balance['total']:
            if balance['AVAX']['free'] > 0.01:  # 設定一個最小AVAX餘額閾值
                current_position = 'AVAX'
        
                
        # 检查价格是否跌破EMA100
        if btc_price < btc_ema100.iloc[-1] or AVAX_price < AVAX_ema100.iloc[-1]:
            print("价格跌破EMA100，转换至USDT")
            self.execute_trade_with_fallback('BTC/USDT', btc_balance, 'USDT')
            self.execute_trade_with_fallback('AVAX/USDT', AVAX_balance, 'USDT')
            target_position = 'USDT'

        # 決策邏輯
        if -self.az <= btc_signal <= self.az and -self.az <= AVAX_signal <= self.az:
            if btc_signal < 0 and AVAX_signal < 0:
                print("信號在中性區且BTC/AVAX信號小於0保持當前持倉")
                target_position = current_position

            elif current_position == 'BTC' and AVAX_btc_signal > 0:
                print("信號在中性區BTC轉換至AVAX")
                self.execute_trade_with_fallback('AVAX/BTC', btc_balance, 'AVAX')
                self.execute_trade_with_fallback('AVAX/USDT', usdt_balance, 'AVAX')
                target_position = 'AVAX'

            elif current_position == 'AVAX' and AVAX_btc_signal < 0:
                print("信號在中性區AVAX轉換至BTC")
                self.execute_trade_with_fallback('AVAX/BTC', AVAX_balance, 'BTC')
                self.execute_trade_with_fallback('BTC/USDT', usdt_balance, 'BTC')
                target_position = 'BTC'

            else:
                print("信號在中性區信號保持當前持倉")
                target_position = current_position
                

        elif btc_signal < 0 and AVAX_signal < 0:
            print("AVAX/BTC訊號為負轉換至USDT")
            self.execute_trade_with_fallback('BTC/USDT', btc_balance, 'USDT')
            self.execute_trade_with_fallback('AVAX/USDT', AVAX_balance, 'USDT')
            target_position = 'USDT'

        else:
            if current_position == 'BTC' and AVAX_btc_signal > 0:
                print("轉換至AVAX")
                self.execute_trade_with_fallback('AVAX/BTC', btc_balance, 'AVAX')
                self.execute_trade_with_fallback('AVAX/USDT', usdt_balance, 'AVAX')
                target_position = 'AVAX'

            elif current_position == 'AVAX' and AVAX_btc_signal < 0:
                print("轉換至BTC")
                self.execute_trade_with_fallback('AVAX/BTC', AVAX_balance, 'BTC')
                self.execute_trade_with_fallback('BTC/USDT', usdt_balance, 'BTC')            
                target_position = 'BTC'
            else:
                if abs(btc_signal - AVAX_signal) > self.signal_threshold:
                    if btc_signal > AVAX_signal:
                        print("signal_threshold轉換至BTC")
                        self.execute_trade_with_fallback('AVAX/BTC', AVAX_balance, 'BTC')
                        self.execute_trade_with_fallback('BTC/USDT', usdt_balance, 'BTC')    
                        target_position = 'BTC'
                    else :
                        print("signal_threshold轉換至AVAX")
                        self.execute_trade_with_fallback('AVAX/BTC', btc_balance, 'AVAX')
                        self.execute_trade_with_fallback('AVAX/USDT', usdt_balance, 'AVAX')                    
                        target_position = 'AVAX'
                else:
                    target_position = current_position


        print(f"BTC滾動回報率: {btc_signal*100:.3f}%, AVAX滾動回報率: {AVAX_signal*100:.3f}%, AVAX/BTC滾動回報率: {AVAX_btc_signal*100:.3f}%")
        print(f"當前BTC價格{btc_price} BTC100EMA {btc_ema100.iloc[-1]}")
        print(f"當前AVAX價格{AVAX_price} AVAX100EMA {AVAX_ema100.iloc[-1]}")    
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
        
# 使用示例
api_key = 'api_key'
secret = 'secret'
password = 'password'
bot = TradingBot(api_key, secret, password)
bot.run()