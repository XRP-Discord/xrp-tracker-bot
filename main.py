import discord
from discord.ext import commands, tasks
import requests
import dotenv
import os
import json
from urllib.parse import quote

BINANCE_API_URL = "https://api.binance.com/"

dotenv.load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="$xrp ", intents=intents)

channel_to_ticker = {}

def load():
    if os.path.exists('saved.json') == False:
        return

    with open('saved.json', "r") as f:
        data = json.load(f)
        for channel_id in data:
            channel_to_ticker[channel_id] = (data[channel_id][0], data[channel_id][1])
    return

def save():
    json.dump(channel_to_ticker, open('saved.json', 'w'))
    return

@tasks.loop(minutes=5)
async def fetch_price():
    tickers = set()
    for channel_id in channel_to_ticker:
        tickers.add(channel_to_ticker[channel_id][0])

    if (len(tickers) == 0):
        return

    tickers_string = ""
    tickers_string += "["
    for ticker in tickers:
        tickers_string += "\"" + ticker + "\","

    tickers_string = tickers_string[:-1]
    tickers_string += ']'
    
    url = BINANCE_API_URL + "api/v3/ticker/24hr?symbols=" + quote(tickers_string)
    try:
        response = requests.get(url, timeout=2)
        json = response.json()

        ticker_to_price = {}
        for ticker in json:
            price = round(float(ticker["lastPrice"]), 3)
            price_change_percent = round(float(ticker["priceChangePercent"]), 1)
            ticker_to_price[ticker["symbol"]] = (price, price_change_percent)

        for channel_id in channel_to_ticker:
            ticker = channel_to_ticker[channel_id][0]
            alias = channel_to_ticker[channel_id][1]
            price = ticker_to_price[ticker][0]
            price_change_percent = ticker_to_price[ticker][1]

            channel = bot.get_channel(int(channel_id))
            plus_minus = price_change_percent > 0 and "+" or ""
            color = '🟠'
            if price_change_percent > 0:
                color = '🟢'
            elif price_change_percent < 0:
                color = '🔴'
    
            await channel.edit(name=f'{color} {alias}{price} ({plus_minus}{price_change_percent}%)')

    except Exception as e:
        print("Error fetching price: " + e)

@bot.event
async def on_ready():
    load()
    fetch_price.start()

@bot.command()
async def monitor(ctx, ticker, alias, channel_id):
    if ctx.author.guild_permissions.administrator == False:
        await ctx.send("Not an admin")
        return

    channel_to_ticker[channel_id] = (ticker, alias)
    save()
    await ctx.send("Adding monitor for ticker `" + ticker + "` on channel `" + channel_id + "`")

@bot.command()
async def monitor_remove(ctx, channel_id):
    if ctx.author.guild_permissions.administrator == False:
        await ctx.send("Not an admin")
        return

    channel_to_ticker.pop(channel_id)
    save()
    await ctx.send("Removing monitor for channel `" + channel_id + "`")

bot.run(os.getenv("DISCORD_BOT_TOKEN"))
