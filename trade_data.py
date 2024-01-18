import ccxt.async_support as ccxt
import asyncio
import pandas as pd
from datetime import datetime, timedelta
from core.trade import TradingBot
import os
import json

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
        df.to_csv(f'./dailydata/{symbol.replace("/", "_")}.csv', index=False) #symbol.replace("/", "_")

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
        await asyncio.sleep(wait_seconds)
        await get_crypto_data()

        # 遍歷目錄中的每個JSON文件
        for filename in os.listdir('./userinfo/'):
            if filename.endswith('.json'):
                file_path = os.path.join('./userinfo/', filename)
                with open(file_path, 'r') as userinfo:
                    data = json.load(userinfo)
                    username = data.get("username")
                    symbol_2 = data.get("symbol_2")
                    user_id = data.get("user_id")
                    if symbol_2 == 'SOL':
                        KlineNum = 9
                        KlineNum2 = 16
                        az = 0.06
                        signal_threshold = 0.08
                        ema = 39
                        ema_2 = 179
                    elif symbol_2 == 'MATIC':
                        KlineNum = 20
                        KlineNum2 = 37
                        az = 0.06
                        signal_threshold = 0.08
                        ema = 79
                        ema_2 = 189
                    api_keys = data.get("api_keys")
                    if "secret" in api_keys:
                        api_key = api_keys["api_key"]
                        secret = api_keys["secret"]
                        password = api_keys["password"]
                        # 打印信息以確認正在處理的文件和用戶
                        print(f"File: {filename}, Username: {username}, symbol_2: {symbol_2}")

                        # 使用從文件中提取的信息創建 TradingBot 實例並運行
                        bot = TradingBot(symbol_2, api_key, secret, password, ema=ema, ema_2=ema_2, KlineNum=KlineNum, KlineNum2=KlineNum2, az=az, signal_threshold=signal_threshold, below_ema=False)
                        try:
                            bot.evaluate_positions_and_trade(symbol_2)  # 運行 bot
                        except:
                            print(f'用戶: {username} ID: {user_id} 交易執行出錯')
                    else:
                        print(f"File: {filename}, Username: {username}, symbol_2: {symbol_2}, Password not found")

# 啟動調度任務
asyncio.run(schedule_task())

