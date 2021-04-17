import json
import discord
from discord.ext import commands
import random

with open("setting.json",mode='r',encoding='utf8') as jfile:
  data=json.load(jfile)

bot = commands.Bot(command_prefix=".")

@bot.command()
async def pic(ctx):
  pic = discord.File('D:\\BOT\\BigMama_BOT\\pic\\2.jpg')
  await ctx.send(File=pic)

@bot.event
async def on_ready():
  print(">> Bot is ONLINE <<")

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


