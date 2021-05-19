import discord
from discord.ext import commands
import sys
sys.path.append('.\BigMama_BOT\core')
from core.classes import Cog_extension

class Main(Cog_extensioin.Cog):


    @commands.command()
    async def ping(self,ctx):
        lag=round(self.bot.latency*1000)
        await ctx.send(f'I\'m very lag...My latency is {lag} ms')

def setup(bot):
    bot.add_cog(Main(bot))