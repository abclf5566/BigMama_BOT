
import ccxt
import pandas as pd
import time
import decimal
import math
from core import tool

def read_csv(filename):
    try:
        # 使用pandas的read_csv函數來讀取CSV文件
        df = pd.read_csv(f'dailydata/{filename}.csv')
        return df
    except FileNotFoundError:
        print(f"{filename}.csv 文件不存在.")
        return None

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
    def __init__(self, symbol_2, api_key, secret, password, KlineNum, KlineNum2, az, signal_threshold, ema, ema_2, below_ema):
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
        self.below_ema = False

    def evaluate_current_position(self):
        # 獲取市場價格
        btc_price = self.exchange.fetch_ticker('BTC/USDT')['last']
        symbol_2_price = self.exchange.fetch_ticker(f'{self.symbol_2}/USDT')['last']

        # 獲取賬戶余額
        balance = self.exchange.fetch_balance()

        # 安全地獲取各資產的余額（如果沒有則返回0）
        btc_balance = balance['BTC'].get('free', 0)
        symbol_2_balance = balance.get(self.symbol_2, {}).get('free', 0)
        usdt_balance = balance['USDT'].get('free', 0)

        # 計算各資產的價值（以USDT為單位）
        btc_value = btc_balance * btc_price
        symbol_2_value = symbol_2_balance * symbol_2_price
        usdt_value = usdt_balance

        # 比較各資產價值，選擇最大的作為當前持倉
        if btc_value > symbol_2_value and btc_value > usdt_value:
            return 'BTC'
        elif symbol_2_value > btc_value and symbol_2_value > usdt_value:
            return self.symbol_2
        else:
            return 'USDT'
        
    def calculate_rolling_returns(self, data, window):
        """
        計算滾動回報率。
        :param data: 包含價格數據的DataFrame。
        :param window: 滾動窗口大小。
        :return: 滾動回報率序列。
        """
        return data['close'].pct_change(window)

    def calculate_moving_average(self, data, window):
        """
        計算MA
        """
        return data['close'].rolling(window=window).mean()

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

    def execute_trade_with_fallback(self, symbol, amount, target_position):
        try:
            # 加載市場信息
            market_info = self.exchange.load_markets()
            symbol_info = market_info['BTC/USDT']
            symbol_2_info = market_info[f'{self.symbol_2}/USDT']

            transaction_amount = amount  # 默認交易數量為amount
            if symbol == f'{self.symbol_2}/BTC' and target_position == self.symbol_2:
                # 使用BTC購買SYMBOL_2
                market_price = self.exchange.fetch_ticker(symbol)['last']
                transaction_amount = truncate(amount / market_price, count_decimal_places(symbol_2_info['precision']['amount']))
                order_info = self.exchange.create_market_buy_order(symbol, transaction_amount)

            elif symbol == f'{self.symbol_2}/BTC' and target_position == 'BTC':
                # 使用BTC購買SYMBOL_2
                order_info = self.exchange.create_market_sell_order(symbol, transaction_amount)

            elif symbol == 'BTC/USDT' and target_position == 'BTC':
                # 使用USDT購買BTC
                market_price = self.exchange.fetch_ticker(symbol)['last']
                transaction_amount = truncate(amount / market_price, count_decimal_places(symbol_info['precision']['amount']))
                order_info = self.exchange.create_market_buy_order(symbol, transaction_amount)

            elif symbol == f'{self.symbol_2}/USDT' and target_position == self.symbol_2:
                # 使用USDT購買SYMBOL_2
                market_price = self.exchange.fetch_ticker(symbol)['last']
                transaction_amount = truncate(amount / market_price, count_decimal_places(symbol_2_info['precision']['amount']))
                order_info = self.exchange.create_market_buy_order(symbol, transaction_amount)

            elif symbol in ['BTC/USDT', f'{self.symbol_2}/USDT'] and target_position == 'USDT':
                # 執行賣出操作
                order_info = self.exchange.create_market_sell_order(symbol, amount)
            else:
                raise ValueError("未知的交易類型或目標持倉")

            client_order_id = order_info['clientOrderId']
            print(f"訂單ID: {client_order_id}, 成功下單: {symbol} 數量 {transaction_amount}")

        except ccxt.InvalidOrder as e:
            print(f"下單失敗，訂單不合法: {e}. 交易嘗試: {symbol} 數量 {transaction_amount}")
        except ccxt.InsufficientFunds as e:
            print(f"下單失敗，余額不足: {e}. 交易嘗試: {symbol} 數量 {transaction_amount}")
        except Exception as e:
            print(f"下單失敗，出現其他錯誤: {e}. 交易嘗試: {symbol} 數量 {transaction_amount}")

    def evaluate_positions_and_trade(self, symbol_2):
        """
        評估持倉並執行交易邏輯
        """
        btc_data = read_csv('BTC_USDT')
        symbol_2_data = read_csv(f'{symbol_2}_USDT')
        symbol_2_btc_data = read_csv(f'{symbol_2}_BTC')

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

        btc_ema = self.calculate_moving_average(btc_data, self.ema)
        symbol_2_ema = self.calculate_moving_average(symbol_2_data, self.ema_2)

        btc_price = btc_data['close'].iloc[-1]  # 最新的BTC收盤價
        symbol_2_price = symbol_2_data['close'].iloc[-1]  # 最新的symbol_2收盤價

        current_position = self.evaluate_current_position()  # 算當前最大持倉幣種 
        new_position = tool.calculate_trade_decision(current_position,self.symbol_2, btc_signal, symbol_2_signal, symbol_2_btc_signal, self.az, self.signal_threshold)

        # 檢查是否嫁得跌破EMA
        if (current_position == 'BTC' and btc_price < btc_ema.iloc[-2]) or (current_position == f'{symbol_2}' and symbol_2_price < symbol_2_ema.iloc[-2]):
            if not self.below_ema:
                print("價格跌破EMA，轉換至USDT")
                new_position = 'USDT'
                self.below_ema = True
        else:
            self.below_ema = False

        # 根據當前持倉和目標持倉決定是否執行交易
        if current_position != new_position:
            if new_position == 'USDT':
                self.execute_trade_with_fallback('BTC/USDT', btc_balance, 'USDT')
                self.execute_trade_with_fallback(f'{self.symbol_2}/USDT', symbol_2_balance, 'USDT')
            elif new_position == 'BTC':
                self.execute_trade_with_fallback(f'{self.symbol_2}/BTC', symbol_2_balance, 'BTC')
                self.execute_trade_with_fallback('BTC/USDT', usdt_balance, 'BTC')
            elif new_position == f'{self.symbol_2}':
                self.execute_trade_with_fallback(f'{self.symbol_2}/BTC', btc_balance, f'{self.symbol_2}')
                self.execute_trade_with_fallback(f'{self.symbol_2}/USDT', usdt_balance, f'{self.symbol_2}')

        print(f"BTC滾動回報率: {btc_signal*100:.3f}%, {symbol_2}滾動回報率: {symbol_2_signal*100:.3f}%, {symbol_2}/BTC滾動回報率: {symbol_2_btc_signal*100:.3f}%")
        print(f"當前BTC價格{btc_price} BTC EMA {btc_ema.iloc[-1]}")
        print(f"當前{symbol_2}價格{symbol_2_price} {symbol_2} EMA {symbol_2_ema.iloc[-1]}")    
        print(f"當前持倉: {current_position}, 目標持倉: {new_position}")