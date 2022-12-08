import os
from os.path import join, dirname
import time

import discord
from discord.ext import commands
from discord_buttons_plugin import *
from discord.utils import get
from dislash import InteractionClient, SelectMenu, SelectOption

dotenv_path = join(dirname(__file__), '.env')
if os.path.isfile(dotenv_path):
    from dotenv import load_dotenv

    load_dotenv(verbose=True)
    load_dotenv(dotenv_path)

TOKEN = os.environ["DISCORD_BOT_TOKEN"]
bot = commands.Bot(intents=discord.Intents.all(), command_prefix="!")
buttons = ButtonsClient(bot)
slash = InteractionClient(bot)

first_record = None
time_reset_emoji = "♻"

# bot起動完了時に実行される処理
@bot.event
async def on_ready():
    print('準備完了')
    await bot.change_presence(activity=discord.Game("Python"))


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
async def start(ctx):
    global first_record
    first_record = None

    await buttons.send(
            "ボタンを押して解答！",
            channel = ctx.channel.id,
            components = [
                ActionRow([
                    Button(
                        label="I got it!", 
                        style=ButtonType().Success, 
                        custom_id="button_clicked",
                        disabled = False
                    )
                ])
            ]
        )
    
    # sended_btn = (await bot.get_channel(ctx.channel.id).history(limit=1).flatten())[0]
    bot_id = ctx.me.id
    t_channel = ctx.channel
    sended_btn = await t_channel.history().get(author__id=bot_id)
    await sended_btn.add_reaction(time_reset_emoji)

@buttons.click
async def button_clicked(ctx):
    global first_record

    record = None
    if not first_record:
        first_record = time.perf_counter()
        record = 0
    else:
        record = time.perf_counter() - first_record

    if ctx.guild.voice_client is not None:
        ctx.guild.voice_client.stop()
        ctx.guild.voice_client.play(discord.FFmpegPCMAudio("./resouce/pinpon.mp3"))

    display_name = None
    members = ctx.guild.members
    for m in members:
        if m.id == ctx.member.id:
            display_name=m.nick
            break
    
    await ctx.reply()
    await ctx.channel.send(f'{display_name} pushed: +{round(record, 2)}s')

# タイマーリセット&ボタン再発行処理
@bot.event
async def on_raw_reaction_add(payload):
    
    if payload.member.bot:
        return
    if payload.emoji.name != time_reset_emoji:
        return

    channel = bot.get_channel(payload.channel_id)
    await channel.send('=====↓ 新しいボタンを使ってください ↓=====')
    
    global first_record
    first_record = None

    await buttons.send(
            "ボタンを押して解答！",
            channel = payload.channel_id,
            components = [
                ActionRow([
                    Button(
                        label="I got it!", 
                        style=ButtonType().Success, 
                        custom_id="button_clicked",
                        disabled = False
                    )
                ])
            ]
        )
    
    sended_btn = (await bot.get_channel(payload.channel_id).history(limit=1).flatten())[0]
    await sended_btn.add_reaction(time_reset_emoji)

@bot.command()
async def summon(ctx):

     # コマンド送信主の入ってるチャンネルを取得
    try:
        v_channel = ctx.author.voice.channel
        await v_channel.connect()
    except AttributeError:
        await ctx.send("コマンドの実行者はボイスチャンネルに入室してください")
        return

@bot.command()
async def kick(ctx):

    if ctx.guild.voice_client is None:
        await ctx.send("Botはボイスチャンネルに入室していません...")
        return
    else:
        await ctx.guild.voice_client.disconnect()

bot.run(TOKEN)
