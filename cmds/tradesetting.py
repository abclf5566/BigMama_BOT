from discord.ui import Modal, TextInput
from discord.ui import Button, View
from core.classes import Cog_extension
import os
import ccxt
import discord
import json

class Trade_setting(Cog_extension):

    class ChoiceView(View):
        def __init__(self, user_id):
            super().__init__(timeout=30)
            self.user_id = user_id
            self.choice = None
            self.modal_sent = False

        @discord.ui.button(label="幫我選 預設選擇 SOL",  style=discord.ButtonStyle.primary, emoji="😎")
        async def choose_for_me_button(self, interaction: discord.Interaction, button: Button):
            self.choice = "SOL"  # 預設選擇 SOL
            self.stop()
            modal = Trade_setting.APIModal(user_id=self.user_id, choice=self.choice)
            await interaction.response.send_modal(modal)

        @discord.ui.button(label="SOL", style=discord.ButtonStyle.secondary)
        async def sol_button(self, interaction: discord.Interaction, button: Button):
            self.choice = "SOL"
            self.stop()
            modal = Trade_setting.APIModal(user_id=self.user_id, choice=self.choice)
            await interaction.response.send_modal(modal)

        @discord.ui.button(label="ETH", style=discord.ButtonStyle.secondary)
        async def eth_button(self, interaction: discord.Interaction, button: Button):
            self.choice = "ETH"
            self.stop()
            modal = Trade_setting.APIModal(user_id=self.user_id, choice=self.choice)
            await interaction.response.send_modal(modal)

        @discord.ui.button(label="MATIC", style=discord.ButtonStyle.secondary)
        async def matic_button(self, interaction: discord.Interaction, button: Button):
            self.choice = "MATIC"
            self.stop()
            modal = Trade_setting.APIModal(user_id=self.user_id, choice=self.choice)
            await interaction.response.send_modal(modal)

        async def interaction_check(self, interaction: discord.Interaction) -> bool:
            return str(interaction.user.id) == self.user_id

        async def on_timeout(self):
            self.choice = None  # 如果超时，则设置选择为 None

    class APIModal(Modal):
        def __init__(self, user_id, choice, title="輸入您的OKX API Key"):
            super().__init__(title=title)
            self.choice = choice #按鈕資訊保存
            self.user_id = user_id
            self.api_key = TextInput(label="API Key ", style=discord.TextStyle.short ,min_length= 36, max_length=36)
            self.secret = TextInput(label="Secret", style=discord.TextStyle.short ,min_length= 32, max_length=32)
            self.password = TextInput(label="Password", style=discord.TextStyle.short ,min_length= 8, max_length=32)

            self.add_item(self.api_key)
            self.add_item(self.secret)
            self.add_item(self.password)

        async def api_test(self, api_key, secret, password):
            print(f"用戶: {self.user_id} 調用api_test")
            exchange = ccxt.okx({
                'apiKey': api_key,
                'secret': secret,
                'password': password,
                'enableRateLimit': True,
            })

            try:
                balance = exchange.fetch_balance()
                if balance['info']['code'] == '0':
                    print(f"用戶: {self.user_id} API 連接成功")
                    return True
            except Exception as e: 
                print(f"用戶: {self.user_id} 調用api_test失敗")
                if os.path.exists(f'./userinfo/{self.user_id}.json'):
                    os.remove(f'./userinfo/{self.user_id}.json')
                print(f'已經移除 {self.user_id} 資訊')
                return False

        async def on_submit(self, interaction: discord.Interaction):
            api_keys = {
                "api_key": self.api_key.value,
                "secret": self.secret.value,
                "password": self.password.value
            }
            user_info = {
                "username": interaction.user.name,
                "user_id": interaction.user.id,
                "discriminator": interaction.user.discriminator,
                "api_keys": api_keys,
                "symbol_2": self.choice #用戶按鈕選擇保存
            }

            try:
                os.makedirs('userinfo', exist_ok=True)
                with open(f'userinfo/{self.user_id}.json', 'w', encoding='utf-8') as f:
                    json.dump(user_info, f, ensure_ascii=False, indent=4)

                if await self.api_test(self.api_key.value, self.secret.value, self.password.value):
                    await interaction.response.send_message("您的信息和 API Key 已成功保存", ephemeral=True)
                else:
                    raise Exception("保存信息/API 調用時出錯")
            except Exception as e:
                print(f"用戶: {self.user_id}保存信息時出錯 {e}")
                error_message = str(e)
                await interaction.response.send_message(f"保存信息時發生錯誤：{error_message}請檢查OKX API", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Trade_setting(bot))
