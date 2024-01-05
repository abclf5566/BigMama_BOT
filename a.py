import discord
from discord.ext import commands
from discord import app_commands
import json

class MyBot(commands.Bot):
    def __init__(self, command_prefix, intents, data):
        super().__init__(command_prefix, intents=intents)
        self.data = data

    async def setup_hook(self):
        self.tree.add_command(hello)
        self.tree.add_command(say)
        self.tree.add_command(test_command)
        await self.tree.sync()

    async def on_ready(self):
        print(">> Bot is ONLINE <<")
        try:
            synced = await self.tree.sync()
            print(f'Synced {len(synced)} command(s)')
        except Exception as e :
            print(e)

    async def on_member_join(self, member):
        channel = self.get_channel(int(self.data['welcome_channel']))
        await channel.send(f'{member} Join!')

    async def on_member_remove(self, member):
        channel = self.get_channel(int(self.data['Leave_channel']))
        await channel.send(f'{member} Leave!')

@bot.tree.command(name="hello", description="hello world")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f'Hey {interaction.user.mention} ! This is a slash command', ephemeral=True)

@bot.tree.command(name="say", description="say world")
@app_commands.describe(thing_to_say='what should I say ?')
async def say(interaction: discord.Interaction, thing_to_say: str):
    await interaction.response.send_message(f"{interaction.user.name} ! said: '{thing_to_say}'")

@bot.tree.command(name='test', description="TEST")
async def test_command(interaction: discord.Interaction):
    await interaction.response.send_message("測試命令被成功執行！")

@bot.command()
async def fuck(ctx):
    await ctx.send("fuck u")

# 主程序
if __name__ == "__main__":
    with open('setting.json', mode='r', encoding='utf8') as jfile:
        data = json.load(jfile)

    # 啟用所有必要的 Intents
    intents = discord.Intents.default()
    intents.messages = True
    intents.guilds = True
    intents.typing = False
    intents.message_content = True

    # 創建和運行機器人實例
    bot = MyBot(command_prefix="$", intents=intents, data=data)
    bot.run(data['token'])
