import json
import discord
from discord.ui import Modal, TextInput
from discord.ext import commands
from discord import app_commands
import os
import ccxt

with open('setting.json',mode='r',encoding='utf8') as jfile:
  data=json.load(jfile)

# 啟用所有必要的 Intents
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.typing = False
intents.message_content = True

bot = commands.Bot(command_prefix="$", intents=intents)

@bot.event
async def on_ready():
  print(">> Bot is ONLINE <<")
  try:
    synced = await bot.tree.sync()
    print(f'Synced {len(synced)} command(s)')
  except Exception as e :
    print(e)

@bot.tree.command(name="hello", description="hello world")
async def hello(interaction: discord.Interaction):
  await interaction.response.send_message(f'Hey {interaction.user.mention} ! THis is a slash command',ephemeral= True)

@bot.tree.command(name="say", description="say world")
@app_commands.describe(thing_to_say= 'what should I say ?')
async def say(interaction: discord.Interaction, thing_to_say: str):
  await interaction.response.send_message(f"{interaction.user.name} ! said: '{thing_to_say}'")

@bot.event
async def on_member_join(member):
  channel = bot.get.channel(int(data['welcome_channel']))
  await channel.send(f'{member}Join!')

@bot.event
async def on_member_remove(member):
  channel = bot.get.channel(int(data['Leave_channel']))
  await channel.send(f'{member}Leave!')

@bot.command()
async def fuck(ctx):
  await ctx.send("fuck u")

# 注冊斜槓命令
@bot.tree.command(name='test', description="TEST")
async def test_command(interaction: discord.Interaction):
    await interaction.response.send_message("測試命令被成功執行！")

class APIModal(Modal):
    def __init__(self, user_id, title="輸入您的OKX API Key"):
        super().__init__(title=title)
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
            "api_keys": api_keys
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
            print(f"用戶{self.user_id}保存信息時出錯 {e}")
            error_message = str(e)
            await interaction.response.send_message(f"保存信息時發生錯誤：{error_message}請檢查OKX API", ephemeral=True)

@bot.tree.command(name='trade', description="Trade command")
async def trade_command(interaction: discord.Interaction):
    modal = APIModal(user_id=str(interaction.user.id))
    await interaction.response.send_modal(modal)

if __name__ == "__main__":
  bot.run(data['token'])


