import pandas as pd

# 假設你的CSV文件名為 'BTC_USDT_1d.csv'
file_name = 'BTC_USDT_1d.csv'

# 讀取CSV文件
df = pd.read_csv(file_name)
data = df['Close'].tolist()  # 假設收盤價在 'Close' 列

class Calculator:
    def calculate_ema(self, data, window):
        return pd.Series(data).ewm(span=window, adjust=False).mean()

    def calculate_rolling_returns(self, data, window):
        """
        計算滾動回報率
        """
        return pd.Series(data).pct_change(window)

calculator = Calculator()

# 設定窗口值
ema_window = 10
rolling_returns_window = 5

# 計算EMA和滾動回報率
ema = calculator.calculate_ema(data, ema_window)
rolling_returns = calculator.calculate_rolling_returns(data, rolling_returns_window)

# 打印結果
print("EMA:\n", ema)
print("\nRolling Returns:\n", rolling_returns)
