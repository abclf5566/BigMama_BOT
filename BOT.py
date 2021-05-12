import json
import discord
from discord.ext import commands
import random as rd

with open("setting.json",mode='r',encoding='utf8') as jfile:
  data=json.load(jfile)

bot = commands.Bot(command_prefix=".")

@bot.event
async def on_ready():
  print(">> Bot is ONLINE <<")

@bot.event
async def on_member_join(member):
  channel = bot.get.channel(841870126588624936)
  await channel.send(f'{member}Join!')

@bot.event
async def on_member_remove(member):
  channel = bot.get.channel(841870126588624936)
  await channel.send(f'{member}Leave!')

@bot.command()
async def fuck(ctx):
  await ctx.send("fuck u")

@bot.command()
async def ping(ctx):
  lag=round(bot.latency*1000)
  await ctx.send(f'我..很LAG 延遲是 {lag} ms')

@bot.command()
async def game(ctx):
  answer=range(0,100)
  num=int(input())


bot.run(data['token'])


