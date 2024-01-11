from discord.ext import commands
from core.classes import Cog_extension

class Main(Cog_extension):

    @commands.command()
    async def ping(self,ctx):
        lag=round(self.bot.latency*1000)
        await ctx.send(f'I\'m very lag...My latency is {lag} ms')

async def setup(bot):
    await bot.add_cog(Main(bot))