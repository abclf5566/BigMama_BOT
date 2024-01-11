from discord.ext import commands
from core.classes import Cog_extension
import random as rd
import json

with open('setting.json',mode='r',encoding='utf8') as jfile:
  data=json.load(jfile)

class React(Cog_extension):
    @commands.command()
    async def pic(self,ctx):
      rd_pic = rd.choice(data['pic'])
      await ctx.send(rd_pic)

async def setup(bot):
    await bot.add_cog(React(bot))