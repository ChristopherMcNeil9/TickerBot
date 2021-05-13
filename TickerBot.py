import discord
import re
import requests
from bs4 import BeautifulSoup

url_base = 'https://www.marketwatch.com/legacy/story/renderquotepeeks?tickers='
# discord token kept in separate file for security purposes
token = open('Tokens.txt').read().rstrip()
client = discord.Client()


@client.event
async def on_message(message):
    if not message.author.bot:
        # gets ticker symbols from user messages
        tickers = re.findall('(\$[a-zA-Z]+)', message.content)
        if tickers:
            for ticker in tickers:
                # creates urls from a given ticker and sends it to server
                ticker = ticker.replace('$', '')
                url = url_base + ticker
                page = requests.get(url).text
                soup = BeautifulSoup(page, 'lxml')

                # gets company name, current price, and percent change from webpage
                try:
                    name = re.findall('[^>]+(?=<)', str(soup.find('div', attrs=['class', 'companyname'])))[1]
                    price = re.findall('[^>]+(?=<)', str(soup.find('span', attrs=['class', 'bgLast'])))[0]
                    percent_change = re.findall('[^>]+(?=<)', str(soup.find('span', attrs=['class', 'bgPercentChange'])))[0]
                    output = name + ' $' + price + ', ' + percent_change
                    # replaces &amp; with only &
                    if 'amp;' in output:
                        output = output.replace('amp;', '')
                except IndexError:
                    output = '$' + ticker + ' is an invalid ticker symbol'

                await message.channel.send(output)


client.run(token)
