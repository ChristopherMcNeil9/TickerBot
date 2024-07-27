from .image_generator import generate_tickerbot_image
from .database import db_libs
from .logger import get_logger
import requests
import discord
import json
import time
import re
import os
import io


class TickerBot(discord.Client):
    async def on_message(self, message):
        logger = get_logger()
        if not message.author.bot:
            author = message.author
            content = message.content
            url_base = 'https://api.tiingo.com/iex?tickers='
            tickers = re.findall(r'((?<=\$)(?![a-zA-Z]+(?:\d|\.[^a-zA-Z]))[a-zA-Z]*\.?[a-zA-Z]+)', content)
            tickers = list(set(tickers))
            logger.info(f'{author}: {content}')

            if content == '$CRWD':
                with open('services/BSOD.png', 'rb') as f:
                    image_file = io.BytesIO(f.read())
                    await message.channel.send(file=discord.File(fp=image_file, filename='BSOD.png'))
                    time.sleep(7)

            if tickers:
                ticker_data = {}
                good_symbols = []
                bad_symbols = []

                # validate tickers and separate good and bad ones
                for ticker in tickers:
                    ticker = ticker.upper()
                    stock_name = db_libs.get_ticker(ticker)
                    if stock_name:
                        good_symbols.append(ticker)
                        ticker_data[ticker] = {
                            'name': stock_name,
                            'price': 'unknown',
                            'change': 'unknown'
                        }
                    else:
                        bad_symbols.append(ticker)

                # get good stocks and check them against API
                if good_symbols:
                    script_dir = os.path.dirname(os.path.abspath(__file__))
                    config_path = os.path.join(script_dir, '../conf/tiingo.conf')
                    config_path = os.path.normpath(config_path)

                    with open(config_path, 'r') as f:
                        config = json.load(f)

                    tiingo_token = config['tiingo']['token']
                    url = url_base + ','.join([ticker for ticker in good_symbols]) + f'&token={tiingo_token}'
                    request = requests.get(url, headers={'Content-Type': 'application/json'})

                    try:
                        request = requests.get(url, headers={'Accept': 'application/json',})
                        json_data = json.loads(request.text)
                    except:
                        json_data = None
                        logger.error('failed to parse API response')

                    changes = []
                    symbols = []
                    prices = []
                    for data in json_data:
                        prev_close = data['prevClose']
                        price_last = data['last']
                        symbols.append(data['ticker'])
                        prices.append(price_last)
                        change = (price_last - prev_close) / abs(prev_close)
                        changes.append(change)

                    for i in range(len(symbols)):
                        if changes[i] is None:
                            changes[i] = 0
                        if prices[i] is None:
                            prices[i] = 0
                        price = format(prices[i], '.2f')
                        change = format(float(changes[i]) * 100, '.2f')
                        ticker_data[symbols[i]]['price'] = f'${price}'
                        ticker_data[symbols[i]]['change'] = f'{change}%'

                    longest_symbol_length = max(len(item) for item in good_symbols)
                    longest_name_length = max(len(item['name']) for item in ticker_data.values())
                    longest_price_length = max(len(item['price']) for item in ticker_data.values())
                    longest_change_length = max(len(item['change']) for item in ticker_data.values())

                    # len('symbol') = 6, len('Company') = 6, len('Price') = 5, len('%Change') = 7,
                    if longest_symbol_length < 6:
                        longest_symbol_length = 6
                    if longest_name_length < 6:
                        longest_name_length = 6
                    if longest_price_length < 5:
                        longest_price_length = 5
                    if longest_change_length < 7:
                        longest_change_length = 7

                    header_1 = 'Symbol'.center(longest_symbol_length + 2)
                    header_2 = '  ' + 'Company'.center(longest_name_length + 2)
                    header_3 = 'Price'.rjust(longest_price_length + 1) + ' '
                    header_4 = ' ' + '%Change'.rjust(longest_change_length)

                    text = '|'.join([header_1, header_2, header_3, header_4]) + '\n\n'
                    for symbol in good_symbols:
                        name = ticker_data[symbol]['name']
                        price = ticker_data[symbol]['price']
                        change = ticker_data[symbol]['change']

                        symbol = symbol.center(longest_symbol_length + 2)
                        name = '  ' + name.ljust(longest_name_length + 2)
                        price = price.rjust(longest_price_length + 1) + ' '
                        change = ' ' + change.rjust(longest_change_length)

                        text += '|'.join([symbol, name, price, change]) + '\n'

                    text = text.rstrip()
                    image = generate_tickerbot_image(text)
                    with io.BytesIO() as image_binary:
                        image.save(image_binary, 'PNG')
                        image_binary.seek(0)
                        await message.channel.send(file=discord.File(fp=image_binary, filename='image.png'))

                if bad_symbols:
                    output_string = ' '.join(bad_symbols) + ' could not be found'
                    await message.channel.send(output_string)


def run():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, '../conf/discord.conf')
    config_path = os.path.normpath(config_path)

    with open(config_path, 'r') as f:
        config = json.load(f)

    token = config['tickerbot']['token']

    intents = discord.Intents.default()
    intents.message_content = True

    client = TickerBot(intents=intents)
    client.run(token, log_handler=None)
