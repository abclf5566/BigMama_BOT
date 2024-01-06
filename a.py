import ccxt

class YourClass:
    def api_test(self, api_key, secret, password):
        exchange = ccxt.okx({
            'apiKey': api_key,
            'secret': secret,
            'password': password,
            'enableRateLimit': True,
        })

        try:
            balance = exchange.fetch_balance()
            print("連接成功，您的帳戶餘額如下：")
            print(balance)
        except Exception as e:
            print("連接失敗，錯誤信息：")
            print(e)

# 使用示例
your_instance = YourClass()
your_instance.api_test("7c497df8-4c9a-4524-aa09-a2ed717b18ea", "66963B0944C4A540F796BE86C9EB6A4C", "!Aa5566288")
