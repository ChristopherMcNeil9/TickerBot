import discord
import re
import requests
from bs4 import BeautifulSoup

# TickerBot uses marketwatch to get all ticker data
url_base = 'https://www.marketwatch.com/legacy/story/renderquotepeeks?tickers='
# discord token kept in separate file for security purposes
token = open('Tokens.txt').read().rstrip()
client = discord.Client()


@client.event
async def on_message(message):
    if not message.author.bot:
        # gets ticker symbols from user messages
        tickers = re.findall(r'((?<=\$)(?![a-zA-Z]+(?:\d|\.[^a-zA-Z]))[a-zA-Z]+\.?[a-zA-Z]+)', message.content)
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
                if len(names[i]) > 32:
                    print(names[i][30])
                    if names[i][30] == '.':
                        names[i] = names[i][0:31].rstrip() + '..'
                    else:
                        names[i] = names[i][0:31].rstrip() + '...'
                # diff is added to all fields inorder to create boxes around each element
                embed_names = embed_names + '```diff\n' + names[i] + '\n```\n'
                embed_prices = embed_prices + '```diff\n$' + prices[i] + '\n```\n'
                # adds space to +/- to percentage value, needed for coloring in diff version of highlights.js
                if '+' in percent_changes[i]:
                    embed_changes = embed_changes + '```diff\n' + percent_changes[i].replace('+', '+ ') + '\n```\n'
                else:
                    embed_changes = embed_changes + '```diff\n' + percent_changes[i].replace('-', '- ') + '\n```\n'

            if len(tickers) != len(names):
                await message.channel.send('one or more tickers was invalid')

            # creates discord embed which contains
            embed = discord.Embed()
            embed = embed.add_field(name='Company', value=embed_names.rstrip(), inline=True).add_field(name='Price', value=embed_prices.rstrip(), inline=True).add_field(name='Percent Change', value=embed_changes.rstrip(), inline=True)
            await message.channel.send(embed=embed)


# consider re-adding check to see what ticker was incorrect?

client.run(token)
