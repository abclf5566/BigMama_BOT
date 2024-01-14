import json
import discord
import os
import asyncio
from cmds.tradesetting import Trade_setting
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

# 注冊斜槓命令
@bot.tree.command(name='test', description="TEST")
async def test_command(interaction: discord.Interaction):
    await interaction.response.send_message("測試命令被成功執行！normal setup")

@bot.tree.command(name='trade', description="Trade command")
async def trade_command(interaction: discord.Interaction):
    view = Trade_setting.ChoiceView(user_id=str(interaction.user.id))
    print('Calling menu...')
    await interaction.response.send_message("請選擇交易幣種:", view=view, ephemeral=True)
    await view.wait()

@bot.command(name='load')
@commands.is_owner()
async def load_extension(ctx, extension):
    try:
        await bot.load_extension(extension)
        await ctx.send(f"Extension {extension} loaded.")
    except Exception as e:
        await ctx.send(f"Error loading extension {extension}: {e}")

@bot.command(name='unload')
@commands.is_owner()
async def unload_extension(ctx, extension):
    try:
        await bot.unload_extension(extension)
        if extension not in bot.extensions:  # 检查扩展是否被卸载
            await ctx.send(f"Extension {extension} unloaded.")
        else:
            await ctx.send(f"Failed to unload extension {extension}.")
    except Exception as e:
        await ctx.send(f"Error unloading extension {extension}: {e}")

@bot.command(name='reload')
@commands.is_owner()
async def reload_extension(ctx, extension):
    try:
        await bot.reload_extension(extension)
        await ctx.send(f"Extension {extension} reloaded.")
    except Exception as e:
        await ctx.send(f"Error reloading extension {extension}: {e}")

async def load_all_extensions(bot):
    for filename in os.listdir('./cmds/'):
        if filename.endswith('.py') and not filename.startswith('__'):
            extension = f'cmds.{filename[:-3]}'
            try:
                await bot.load_extension(extension)
                print(f'Loaded extension: {extension}')
            except Exception as e:
                print(f'Failed to load extension {extension}.', e)

async def main():
    await load_all_extensions(bot)
    await bot.start(data['token'])

if __name__ == "__main__":
    asyncio.run(main())