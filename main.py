import os
from os.path import join, dirname

import discord
from discord.ext import commands

import requests
import aiohttp
import pprint

dotenv_path = join(dirname(__file__), '.env')
if os.path.isfile(dotenv_path):
    from dotenv import load_dotenv

    load_dotenv(verbose=True)
    load_dotenv(dotenv_path)

TOKEN = os.environ["DISCORD_BOT_TOKEN"]
bot = commands.Bot(intents=discord.Intents.all(), command_prefix="!")

AuthB = "Bot " + TOKEN

headers = {
    "Authorization": AuthB
}

# bot起動完了時に実行される処理

@bot.event
async def on_ready():
    print('準備完了')
    await bot.change_presence(activity=discord.Game("Python🐍"))


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

    # new_msg = await ctx.send(content="something command")
    normal_url = returnNormalUrl(ctx.channel.id)
    json = {
            "content": "Hello World",
            "components": [
                {
                    "type": 1,
                    "components": [
                        {
                            "type": 2,
                            "label": "I got it!",
                            "style": 1,
                            "custom_id": "click_one",
                        }
                    ]

                }
            ]
        }
    r = requests.post(normal_url, headers=headers, json=json)
    # await new_msg.add_reaction("✅")

def returnNormalUrl(channelId):
    return "https://discordapp.com/api/channels/" + str(channelId) + "/messages"

async def notify_callback(id, token):
    url = "https://discord.com/api/v8/interactions/{0}/{1}/callback".format(id, token)
    json = {
        "type": 6
    }
    async with aiohttp.ClientSession() as s:
        async with s.post(url, json=json) as r:
            if 200 <= r.status < 300:
                return

async def on_socket_response(msg):
    if msg["t"] != "INTERACTION_CREATE":
        return

    pprint(msg)
    custom_id = msg["d"]["data"]["custom_id"]

    if custom_id == "click_one":
        normal_url = returnNormalUrl(msg["d"]["channel_id"]) #returnNormalUrl関数の定義はこの記事のどこかにあるよ
        json = {
            "content": "Push button_1"
        }
        r = requests.post(normal_url, headers=headers, json=json)
        await notify_callback(msg["d"]["id"], msg["d"]["token"]) #notify_callback関数は後で説明するよ

bot.run(TOKEN)
