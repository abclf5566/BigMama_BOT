import json
import discord
from discord.ext import commands
import random as rd
import os


with open('setting.json',mode='r',encoding='utf8') as jfile:
  data=json.load(jfile)

bot = commands.Bot(command_prefix="!",intents=None)

@bot.event
async def on_ready():
  print(">> Bot is ONLINE <<")

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

@bot.command()
async def game(ctx):
  answer=range(0,100)
  num=int(input())

for filename in os.listdir('../BigMama_BOT/cmds'):
  if filename.endswith('.py') and not(filename.startswith('__')):
    bot.load_extension(filename[:-3])

if __name__ == "__main__":
  bot.run(data['token'])


