import ccxt.async_support as ccxt
import asyncio
import csv
from datetime import datetime
import schedule
import time

async def fetch_data(symbol):
    exchange = ccxt.binance()  # 创建交易所实例
    candles = await exchange.fetch_ohlcv(symbol, '1m', limit=300)  # 获取 300 条 K 线数据
    await exchange.close()
    return symbol, candles

async def main():
    symbols = ['BTC/USDT', 'ETH/USDT', 'MATIC/USDT', 'SOL/USDT']
    tasks = [fetch_data(symbol) for symbol in symbols]
    results = await asyncio.gather(*tasks)

    # 将数据保存到 CSV
    for symbol, data in results:
        filename = f'{symbol.replace("/", "_")}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            for candle in data:
                writer.writerow(candle)

def job():
    asyncio.run(main())
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

# 计划每天凌晨 00:00:01 执行任务
schedule.every().day.at(f"{formatted_time}").do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
