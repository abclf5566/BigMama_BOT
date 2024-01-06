import json
import discord
from discord.ui import Button, View, Modal, TextInput
from discord.ext import commands
from discord import app_commands
import os

with open('setting.json',mode='r',encoding='utf8') as jfile:
  data=json.load(jfile)

# 啟用所有必要的 Intents
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.typing = False
intents.message_content = True
# 使用 intents 創建機器人實例
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

# 注冊斜杠命令
@bot.tree.command(name='test', description="TEST")
async def test_command(interaction: discord.Interaction):
    await interaction.response.send_message("測試命令被成功執行！")

class APIModal(Modal):
    def __init__(self, user_id, title="輸入您的 API Key"):
        super().__init__(title=title)
        self.user_id = user_id
        self.api_key1 = TextInput(label="API Key ", style=discord.TextStyle.short ,min_length= 36, max_length=36)
        self.api_key2 = TextInput(label="Secret", style=discord.TextStyle.short ,min_length= 32, max_length=32)
        self.api_key3 = TextInput(label="Password", style=discord.TextStyle.short ,min_length= 8, max_length=32)

        self.add_item(self.api_key1)
        self.add_item(self.api_key2)
        self.add_item(self.api_key3)

    async def on_submit(self, interaction: discord.Interaction):
        api_keys = {
            "api_key1": self.api_key1.value,
            "api_key2": self.api_key2.value,
            "api_key3": self.api_key3.value
        }
        user_info = {
            "username": interaction.user.name,
            "user_id": interaction.user.id,
            "discriminator": interaction.user.discriminator,
            "api_keys": api_keys
        }
        try:
            os.makedirs('USERINFO', exist_ok=True)
            with open(f'USERINFO/{self.user_id}.json', 'w', encoding='utf-8') as f:
                json.dump(user_info, f, ensure_ascii=False, indent=4)
            await interaction.response.send_message("您的信息和 API Key 已保存", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"保存信息时发生错误：{e}", ephemeral=True)


@bot.tree.command(name='trade', description="Trade command")
async def trade_command(interaction: discord.Interaction):
    modal = APIModal(user_id=str(interaction.user.id))
    await interaction.response.send_modal(modal)

if __name__ == "__main__":
  bot.run(data['token'])


