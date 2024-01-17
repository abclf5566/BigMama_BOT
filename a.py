import ccxt
import decimal
import math
import pandas as pd
import csv
import os
import json

#folder_path = './userinfo/'


# 遍歷目錄中的每個JSON文件
for filename in os.listdir('./userinfo/'):
    if filename.endswith('.json'):
        file_path = os.path.join('./userinfo/', filename)
        with open(file_path, 'r') as userinfo:
            data = json.load(userinfo)
            username = data.get("username")
            symbol_2 = data.get("symbol_2")
            api_keys = data.get("api_keys")
            if "secret" in api_keys:
                api_key = api_keys["api_key"]
                secret = api_keys["secret"]
                password = api_keys["password"]
                print(f"File: {filename}, Username: {username}, symbol_2: {symbol_2}, Password: {password}, api_key: {api_key}")
            else:
                print(f"File: {filename}, Username: {username}, symbol_2: {symbol_2}, Password not found")

# # 打開CSV文件
# with open('your_file.csv', 'r', newline='') as csvfile:
#     # 創建CSV讀取器
#     csvreader = csv.reader(csvfile)
    
#     # 迭代每一行
#     for row in csvreader:
#         # 在這裡你可以處理每一行的數據
#         print(row)


# def calculate_ema(data, window):
#     return pd.Series([x[4] for x in data]).ewm(span=window, adjust=False).mean()

# btc_ema = calculate_ema()

