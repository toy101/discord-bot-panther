import os
from os.path import join, dirname

# import discord
from discord.ext import commands

dotenv_path = join(dirname(__file__), '.env')
if os.path.isfile(dotenv_path):
    from dotenv import load_dotenv

    load_dotenv(verbose=True)
    load_dotenv(dotenv_path)

TOKEN = os.environ["DISCORD_BOT_TOKEN"]
bot = commands.Bot(command_prefix="!")

# bot起動完了時に実行される処理

@bot.event
async def on_ready():
    print('準備完了')


@bot.event
async def on_guild_join(guild):
    print("サーバーに参加")

    await guild.system_channel.send(content="Hello!")

# メッセージ受信時に実行される処理

@bot.event
async def on_message(message):
    # on_messageイベントの取得とコマンド機能を併用する際に必要な処理
    await bot.process_commands(message)


@bot.command()
async def cmd(ctx):

    new_msg = await ctx.send(content="something command")
    await new_msg.add_reaction("✅")

bot.run(TOKEN)
