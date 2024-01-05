import json
import discord
from discord.ext import commands
from discord import app_commands

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


# @bot.command()
# async def game(ctx):
#   answer=range(0,100)
#   num=int(input())

# for filename in os.listdir('../BigMama_BOT/cmds'):
#   if filename.endswith('.py') and not(filename.startswith('__')):
#     bot.load_extension(filename[:-3])

if __name__ == "__main__":
  bot.run(data['token'])


