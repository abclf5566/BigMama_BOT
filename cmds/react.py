import discord
from discord.ext import commands
import sys
sys.path.append('.\BigMama_BOT\core')
from core.classes import Cog_extension
import random as rd
import json

with open('setting.json',mode='r',encoding='utf8') as jfile:
  data=json.load(jfile)

class React(Cog_extension):
    @cammands.command()
    async def pic(self,ctx):
      rd_pic = rd.choice(data['pic'])
      await ctx.send(rd_pic)

def setup(bot):
    bot.add_cog(React(bot))