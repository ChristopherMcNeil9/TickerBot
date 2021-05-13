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
            # creates urls from a given ticker and sends it to server
            # all tickers sent at once via comma separated list at end of URL
            url = url_base + ','.join([ticker.replace('$', '') for ticker in tickers])
            soup = BeautifulSoup(requests.get(url).text, 'lxml')

            # gets company name, current price, and percent change from webpage
            names = re.findall('[^>]+(?=</a>)', str(soup.findAll('div', attrs=['class', 'companyname'])))
            prices = re.findall('[^>]+(?=</span>)', str(soup.findAll('span', attrs=['class', 'bgLast'])))
            percent_changes = re.findall('[^>]+(?=</span>)', str(soup.findAll('span', attrs=['class', 'bgPercentChange'])))

            for i in range(len(names)):
                output = names[i] + ' $' + prices[i] + ', ' + percent_changes[i]
                # replaces &amp; with only &
                if 'amp;' in output:
                    output = output.replace('amp;', '')
                await message.channel.send(output)

            if len(tickers) != len(names):
                await message.channel.send('one or more tickers was invalid')

# consider re-adding check to see what ticker was incorrect?

client.run(token)
