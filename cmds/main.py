import discord
from discord.ext import commands

class Main(commands.cog):
    def __int__(self,bot):
        self.bot = bot

    @commands.command()
    async def ping(self,ctx):
      lag=round(self.bot.latency*1000)
      await ctx.send(f'我..很LAG 延遲是 {lag} ms')

def setup(bot):
    bot.add_cog(Main(bot))