# xrp-tracker-bot

## Requirements

* Python3
* [Discord Bot](https://discord.com/developers/applications) + Token

## Installation instructions

```bash
python3 -m venv .venv
source ./venv/bin/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## Running the bot

Before running the bot, make sure you have configured all the fields in `.env`

Run the bot:

```bash
python main.py
```

## Usage

To start tracking a ticker on Binance (`XRPEUR`, `XRPUSDT`, etc.), use the following chat command:

```
$xrp monitor XRPUSDT $ 1171509693873664010
```

* `XRPUSDT` is the ticker
* `$` is the alias put in front of the price, e.g.: `$x.xx`
* `1171509693873664010` is the channel id, can be a text channel or a voice channel

Prices are automatically updated every 5 minutes.

To stop tracking a ticker, use the chat command:

```
$xrp monitor_remove 1171509693873664010
```

* `1171509693873664010` is the channel id


