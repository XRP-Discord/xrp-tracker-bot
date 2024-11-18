# xrp-tracker-bot

## Requirements

* Python3
* [Discord Bot](https://discord.com/developers/applications) + Token

## Installation instructions

```bash
python3 -m venv .venv
./venv/bin/pip install -r requirements.txt
cp .env.example .env
```

## Running the bot

Before running the bot, make sure you have configured all the fields in `.env`

Run the bot:

```bash
./venv/bin/python main.py
```

## Usage

To start tracking a ticker on Binance (`XRPEUR`, `XRPUSDT`, etc.), use the following chat command:

```
$xrp monitor_add <ticker> <alias> <decimals> <channel_id>
```

e.g.:

```
$xrp monitor_add XRPUSDT $ 3 1171509693873664010
```

Prices are automatically updated every 5 minutes.

To stop tracking a ticker, use the chat command:

```
$xrp monitor_remove <channel_id>
```


