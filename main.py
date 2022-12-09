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
target_txt_channel = None
time_reset_emoji = "♻"

# bot起動完了時に実行される処理
@bot.event
async def on_ready():
    print('準備完了')
    await bot.change_presence(activity=discord.Game("Python"))


@bot.event
async def on_guild_join(guild):
    print("サーバーに参加")

    embed=discord.Embed(title="Hello World", description="I'm Python-Answer-Observer, Panther", color=0x404040)
    
    embed.add_field(name="```!start```", value="時間計測&解答ボタンの発行", inline=False)
    embed.add_field(name="♻", value="計測リセット&新しいボタンの発行", inline=False)
    embed.add_field(name="```!summon```", value="ボイスチャンネルに呼び出し（解答ボタンを押すとSEが流れます）", inline=False)
    embed.add_field(name="```!kick```", value="ボイスチャンネルからの退出", inline=False)
    embed.add_field(name="```!target```", value="解答者ログを流すテキストチャンネルを指定できます", inline=False)
    embed.set_footer(text="made by 登生",
                     icon_url="https://avatars.githubusercontent.com/u/45931528?v=4")
    await guild.system_channel.send(embed=embed)

# メッセージ受信時に実行される処理
@bot.event
async def on_message(message):
    # on_messageイベントの取得とコマンド機能を併用する際に必要な処理
    await bot.process_commands(message)

@bot.command()
async def desc(ctx):

    embed=discord.Embed(title="使い方", color=0x404040)
    
    embed.add_field(name="```!start```", value="時間計測&解答ボタンの発行", inline=False)
    embed.add_field(name="♻", value="計測リセット&新しいボタンの発行", inline=False)
    embed.add_field(name="```!summon```", value="ボイスチャンネルに呼び出し（解答ボタンを押すとSEが流れます）", inline=False)
    embed.add_field(name="```!kick```", value="ボイスチャンネルからの退出", inline=False)
    embed.add_field(name="```!target```", value="解答者ログを流すテキストチャンネルを指定できます", inline=False)
    
    await ctx.send(embed=embed)

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

@bot.command()
async def target(ctx):
    global target_txt_channel

    target_txt_channel = ctx.channel
    await target_txt_channel.send("解答者ログはこちらのチャンネルに流れます(解除コマンド: `!default`)")

@bot.command()
async def default(ctx):
    global target_txt_channel

    target_txt_channel = None
    await ctx.channel.send("解答者ログはボタンが送信されたチャンネルに流れます")

@buttons.click
async def button_clicked(ctx):
    global first_record
    global target_txt_channel

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
            if m.nick:
                display_name=m.nick
            else:
                display_name=m.name
            break
    
    await ctx.reply()

    t_channel = None
    if target_txt_channel:
        t_channel = target_txt_channel
    else:
        t_channel = ctx.channel
    await t_channel.send(f'{display_name} pushed: +{round(record, 2)}s')

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

    if target_txt_channel:
        await target_txt_channel.send('=====↓ Next Question ↓=====')

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

@bot.command()
async def judge(ctx):

    await buttons.send(
            "司会用ボタン",
            channel = ctx.channel.id,
            components = [
                ActionRow([
                    Button(
                        label="正解", 
                        style=ButtonType().Primary, 
                        custom_id="correct_clicked",
                        disabled = False
                    ),
                    Button(
                        label="不正解", 
                        style=ButtonType().Danger,
                        custom_id="incorrect_clicked",
                        disabled = False
                    )
                ])
            ]
        )

@buttons.click
async def correct_clicked(ctx):
    if ctx.guild.voice_client is None:
        await ctx.channel.send("このボタンを使うためには`!summon`コマンドでボイスチャンネルに入室させてください")
    else:
        ctx.guild.voice_client.stop()
        ctx.guild.voice_client.play(discord.FFmpegPCMAudio("./resouce/correct.mp3"))

    await ctx.reply()

@buttons.click
async def incorrect_clicked(ctx):
    if ctx.guild.voice_client is None:
        await ctx.channel.send("このボタンを使うためには`!summon`コマンドでボイスチャンネルに入室させてください")
    else:
        ctx.guild.voice_client.stop()
        ctx.guild.voice_client.play(discord.FFmpegPCMAudio("./resouce/incorrect.mp3"))

    await ctx.reply()


bot.run(TOKEN)
