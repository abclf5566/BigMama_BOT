from discord.ext import commands
from core.classes import Cog_extension

class Trade(Cog_extension):

    @commands.command()
    async def fuck(self, ctx):
        await ctx.send("fuck uasd")

async def setup(bot):
    await bot.add_cog(Trade(bot))
