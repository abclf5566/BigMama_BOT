import ccxt

exchange = ccxt.binance()

amount = 0.1234568791918
symbol = 'ETH/USDT'

market_info = exchange.load_markets()
symbol_info = market_info[symbol]
amount_value = symbol_info['precision']['amount']
format_amount = exchange.amount_to_precision(symbol, amount)
print(format_amount)
print(amount_value)