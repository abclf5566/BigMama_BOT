from discord.ext import commands
import ccxt
import pandas as pd
import time
from datetime import datetime


class Cog_extension(commands.Cog):
    def __int__(self,bot):
        self.bot=bot
