import re
import time
import discord
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

# TickerBot uses marketwatch to get all ticker data
url_base = 'https://www.marketwatch.com/legacy/story/renderquotepeeks?tickers='
# discord token kept in separate file for security purposes
token = open('Tokens.txt').read().rstrip()
client = discord.Client()


def binary_search(ticker, low, high, array):
    if high >= low and not low == len(array):
        mid = (high + low) // 2
        if array[mid].split('|')[0] == ticker:
            return array[mid]
        elif array[mid].split('|')[0] > ticker:
            return binary_search(ticker, low, mid-1, array)
        else:
            return binary_search(ticker, mid+1, high, array)
    else:
        return 'N/A'


def update_files():
    while True:
        dt = datetime.now() + timedelta(hours=24)
        for url in ['http://ftp.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt', 'http://ftp.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt']:
            data = requests.get(url).text.rstrip()
            # removes everything before final '/' in url as filename
            output = open(url.rsplit('/', 1)[1], 'w')
            output.write(data)
            output.close()
        while datetime.now() < dt:
            # check if 24 hours have passed every 15 minutes
            time.sleep(15*60)


@client.event
async def on_message(message):
    if not message.author.bot:
        # gets ticker symbols from user messages
        tickers = re.findall(r'((?<=\$)(?![a-zA-Z]+(?:\d|\.[^a-zA-Z]))[a-zA-Z]*\.?[a-zA-Z]+)', message.content)
        if tickers:
            # creates urls from a given ticker and sends it to server
            # all tickers sent at once via comma separated list at end of URL
            url = url_base + ','.join([ticker for ticker in tickers])
            soup = BeautifulSoup(requests.get(url).text, 'lxml')

            # gets company name, current price, and percent change from webpage
            names = re.findall('[^>]+(?=</a>)', str(soup.findAll('div', attrs=['class', 'companyname'])))
            prices = re.findall('[^>]+(?=</span>)', str(soup.findAll('span', attrs=['class', 'bgLast'])))
            percent_changes = re.findall('[^>]+(?=</span>)', str(soup.findAll('span', attrs=['class', 'bgPercentChange'])))

            embed_names, embed_prices, embed_changes = '', '', ''
            for i in range(len(names)):
                # replaces &amp; with only &
                if 'amp;' in names[i]:
                    names[i] = names[i].replace('amp;', '')
                # truncates names early to prevent multiline overflow
                if len(names[i]) > 26:
                    if names[i][24] == '.':
                        names[i] = names[i][0:25].rstrip() + '..'
                    else:
                        names[i] = names[i][0:25].rstrip() + '...'
                # diff is added to all fields inorder to create boxes around each element
                embed_names = embed_names + '```diff\n' + names[i] + '\n```\n'
                embed_prices = embed_prices + '```diff\n$' + prices[i] + '\n```\n'
                # adds space to +/- to percentage value, needed for coloring in diff version of highlights.js
                if '+' in percent_changes[i]:
                    embed_changes = embed_changes + '```diff\n' + percent_changes[i].replace('+', '+ ') + '\n```\n'
                else:
                    embed_changes = embed_changes + '```diff\n' + percent_changes[i].replace('-', '- ') + '\n```\n'

            if len(tickers) != len(names):
                for ticker in tickers:
                    ticker = ticker.upper()
                    # checks ticker against list of nasdaq stocks ~5000 stocks
                    stock_list = open('nasdaqlisted.txt').read().split('\n')[1:-1]
                    stock = binary_search(ticker, 0, len(stock_list), stock_list)
                    # if not nasdaq listed, check against other exchanges ~6000 stocks
                    if stock == 'N/A':
                        stock_list = open('otherlisted.txt').read().split('\n')[1:-1]
                        stock = binary_search(ticker, 0, len(stock_list), stock_list)
                        if stock == 'N/A':
                            await message.channel.send('$' + ticker + ' is an invalid ticker')
            # creates discord embed which contains
            if len(names) > 0:
                embed = discord.Embed()
                embed = embed.add_field(name='Company', value=embed_names.rstrip(), inline=True).add_field(name='Price', value=embed_prices.rstrip(), inline=True).add_field(name='Percent Change', value=embed_changes.rstrip(), inline=True)
                await message.channel.send(embed=embed)

client.run(token)
update_files()
