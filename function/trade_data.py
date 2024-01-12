import ccxt.async_support as ccxt
import asyncio
import pandas as pd
from datetime import datetime, timedelta

async def fetch_data(exchange, symbol):
    try:
        data = await exchange.fetch_ohlcv(symbol, '1d', limit=300)
        return pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    finally:
        await exchange.close()

async def get_crypto_data():
    # 定義幣種列表
    symbols = ['BTC/USDT', 'ETH/USDT', 'MATIC/USDT', 'SOL/USDT', 'ETH/BTC', 'MATIC/BTC', 'SOL/BTC']

    # 使用異步獲取數據
    tasks = [fetch_data(ccxt.binance(), symbol) for symbol in symbols]
    data = await asyncio.gather(*tasks)

    # 數據處理邏輯（例如保存到 CSV 文件）
    for i, symbol in enumerate(symbols):
        df = data[i]
        df.to_csv(f'./dailydata/{symbol.replace("/", "_")}.csv', index=False)

async def fetch_server_time():
    exchange = ccxt.binance()
    try:
        server_timestamp = await exchange.fetch_time()
    finally:
        await exchange.close()
    return datetime.utcfromtimestamp(server_timestamp / 1000)

async def schedule_task():
    while True:
        server_time = await fetch_server_time()
        # 計算到下一個 00:00:01 的時間差
        next_run = (server_time + timedelta(days=1)).replace(hour=0, minute=0, second=1, microsecond=0)
        wait_seconds = (next_run - server_time).total_seconds()
        print(f"下次執行時間：{next_run} UTC，等待時間：{wait_seconds}秒")
        await asyncio.sleep(6)
        await get_crypto_data()

# 啟動調度任務
asyncio.run(schedule_task())
