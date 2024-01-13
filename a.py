import ccxt
import decimal

# 初始化Binance
exchange = ccxt.okx({
    'apiKey': '0de1ec2d-9261-4915-9104-519294dd9c7e',
    'secret': 'F58CBB3F57E902C0FF702C33F05008C0',
    'password': '!Aa5566288'
})

def count_decimal_places(value):
    # 將數值轉換為 Decimal 以避免浮點數的不精確性
    value_decimal = decimal.Decimal(str(value))
    # 取得小數部分
    decimal_part = value_decimal.as_tuple().exponent
    # 計算小數位數，如果沒有小數則為0
    return abs(decimal_part) if decimal_part < 0 else 0

market_info = exchange.load_markets()
symbol_info = market_info['BTC/USDT']

precision_amount = symbol_info['precision']['amount']

decimal_places = count_decimal_places(precision_amount)
print(precision_amount)
print("小數點後位數:", decimal_places)

precision_amount = symbol_info['precision']['amount']
decimal_places = abs(decimal.Decimal(str(precision_amount)).as_tuple().exponent) if decimal.Decimal(str(precision_amount)).as_tuple().exponent < 0 else 0

print(precision_amount)
print("小數點後位數:", decimal_places)