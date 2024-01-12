import ccxt
from datetime import datetime

# 创建币安交易所对象
exchange = ccxt.binance()

# 获取币安交易所的服务器时间
server_time_ms = exchange.fetch_time()

# 将毫秒时间戳转换为秒
server_time_sec = server_time_ms / 1000

# 将时间戳转换为可读的时间格式
formatted_time = datetime.utcfromtimestamp(server_time_sec).strftime('%Y-%m-%d %H:%M:%S')

# 打印可读的时间格式
print("Binance服务器时间:", formatted_time)
