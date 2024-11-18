import discord
from discord.ext import commands, tasks
from urllib.parse import quote

import requests
import dotenv
import os
import json
import jsonpickle

BINANCE_API_URL = "https://api.binance.com/"
SAVE_FILENAME = "save.json"

dotenv.load_dotenv()

channel_to_monitor = {}

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="$xrp ", intents=intents)

class Monitor:
    def __init__(self, ticker, alias, decimals = 3):
        self.ticker = ticker
        self.alias = alias
        self.decimals = decimals
    
    def __json__(self):
        return {
            "ticker": self.ticker,
            "alias": self.alias,
            "decimals": self.decimals
        }

def write_save():
    with open(SAVE_FILENAME, 'w') as f:
        f.write(jsonpickle.encode(channel_to_monitor))
        
def load_save():
    if os.path.exists(SAVE_FILENAME) == False:
        return

    with open(SAVE_FILENAME, 'r') as f:
        data = json.load(f)
        for channel_id in data:
            monitor = data[channel_id]
            channel_to_monitor[channel_id] = Monitor(monitor["ticker"], monitor["alias"])
            print(f'Monitor loaded: {channel_to_monitor[channel_id].ticker}')

@bot.command()
async def monitor_add(ctx, ticker, alias, decimals, channel_id): 
    if ctx.author.guild_permissions.administrator == False:
        await ctx.send("Not an admin")
        return

    channel_to_monitor[channel_id] = Monitor(ticker, alias, decimals)
    write_save()
    await ctx.send("Adding monitor for ticker `" + ticker + "` on channel `" + channel_id + "`")


@bot.command()
async def monitor_remove(ctx, channel_id):
    if ctx.author.guild_permissions.administrator == False:
        await ctx.send("Not an admin")
        return

    channel_to_monitor.pop(channel_id)
    write_save()
    await ctx.send("Removed monitor on channel `" + channel_id + "`")

@tasks.loop(minutes=5.5)
async def update_monitors():
    print("Updating monitors")
    
    tickers = set()
    tickers_string = ""
    
    if len(channel_to_monitor) == 0:
        return

    for channel_id in channel_to_monitor:
        monitor = channel_to_monitor[channel_id]
        tickers.add(monitor.ticker)
    
        tickers_string = ""
        tickers_string += "["
        for ticker in tickers:
            tickers_string += "\"" + ticker + "\","
    
        tickers_string = tickers_string[:-1]
        tickers_string += ']'
    
    url = BINANCE_API_URL + "api/v3/ticker/24hr?symbols=" + quote(tickers_string)

    ticker_to_price = {} 
    try:
        data = requests.get(url).json()
        ticker_to_price = {}
        for ticker in data:
            price = float(ticker["lastPrice"])
            price_change_percent = round(float(ticker["priceChangePercent"]), 1)
            ticker_to_price[ticker["symbol"]] = (price, price_change_percent)
    except Exception as e:
        print("Error fetching price: " + str(e))

    for channel_id in channel_to_monitor:
        monitor = channel_to_monitor[channel_id]
        try:
            ticker = ticker_to_price[monitor.ticker]

            price = f'{ticker[0]:.{monitor.decimals}f}'
            change_percent = ticker[1]
    
            channel = bot.get_channel(int(channel_id))
            plus_minus = change_percent > 0 and "+" or ""
            color = '🟠'
            if change_percent > 0:
                color = '🟢'
            elif change_percent < 0:
                color = '🔴'
    
            await channel.edit(name=f'{color} {monitor.alias}{price} ({plus_minus}{change_percent}%)')
        except Exception as e:
            print("Error changing channel: " + str(e))

@bot.event
async def on_ready():
    update_monitors.start()

load_save()
bot.run(os.getenv("DISCORD_BOT_TOKEN"))
