import os
import datetime
import random
import yfinance as yf
import plotly.express as px
from dotenv import load_dotenv
import discord
import matplotlib.pyplot as plt
import requests

import aiocron

import sub_bot


# 1
from discord.ext import commands

top_stock_companies = ['AAPL', 'GOOGL', 'TSLA', 'MSFT', 'AMZN', 'FB', 'BRK-B', 'SPY',
                       'BABA', 'JPM', 'WMT', 'V', 'T', 'UNH', 'PFE', 'INTC', 'VZ', 'ORCL']

df = None
df_not_none = False
count = 0
random_company = ''
nrows = 0

if not os.path.exists("images"):
    os.mkdir("images")

load_dotenv()
TOKEN = os.getenv('MTE2NDQ3NjAxOTQ1ODE4NzI4NA.G8M6s2.XAxo8_esrIQFjL796278gZ60rJQmCT3OwJ5oz4')

# 2
import discord
from discord.ext import commands

# Define your intents
intents = discord.Intents().all()

# Create an instance of the bot with the defined intents
bot = commands.Bot(command_prefix='!', intents=intents)

# Rest of your bot code



@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')


@bot.command(name="commands", help="List all available commands")
async def list_commands(ctx):
    commands_list = [
        "1.!get-list: Displays a list of predefined stock companies.",
        "2.!prev-stock-data [stock_company]: Retrieves and displays the previous day's stock data for a specified company. It also generates and sends a plot.",
        "3.!daily-trade-updates [stock_company]: Sends a daily trade update plot for a specified company.",
        "4.!stock-history [company1] [company2] ...: Sends a historical plot for one or more specified companies.",
        "5.!stock-history-bw-dates [company] [start_date] [end_date]: Sends a historical plot for a specified company within a specified date range.",
        "6.!create-channel [channel_name]: Creates a new text channel (admin-only command).",
        "7.!current-stock-value [company_name]:Displays the real time stock value for an particular company."
        ]
    help_message = "\n".join(commands_list)

    await ctx.send(f"```{help_message}```")


@bot.command(name="get-list", help="Check list of companies for which stock details can be fetched.")
async def get_list(ctx):
    await ctx.send(top_stock_companies)


@bot.command(name="prev-stock-data", help="Check previous day stock data of a company.")
async def stock_data(ctx, stock_company):

    if stock_company in top_stock_companies:
        stock_company_df = yf.download(stock_company, period="2d")
        msg = create_msg(stock_company, stock_company_df)

        stock_company_df = yf.download(
            stock_company, period="2d", interval="1m")
        stock_company_df[0:390].plot(y='Close', linewidth=0.85)

        plt.xlabel('Datetime')
        plt.ylabel('Close')
        plt.title('Stock prices of {company} for previous day'.format(
            company=stock_company))

        plt.savefig('images/stock_previous_day.png')

        await ctx.send(msg, file=discord.File('images/stock_previous_day.png'))

        os.remove('images/stock_previous_day.png')
    else:
        await ctx.send("Stock data for {stockCompany} doesn't exist!".format(stockCompany=stock_company))


@bot.command(name="daily-trade-updates", help="Check latest detailed plot of a company.")
async def get_daily_trade_updates_plot(ctx, stock_company):

    if stock_company in top_stock_companies:
        await sub_bot.send_daily_trade_updates_plot(stock_company, ctx)
    else:
        await ctx.send("Stock data plot for {stockCompany} doesn't exist!".format(stockCompany=stock_company))


@bot.command(name="stock-history", help="Check historical plot of a company(s).")
async def get_stock_history(ctx, *args):
    if len(args) >= 1:
        if set(args).issubset(tuple(top_stock_companies)):
            await sub_bot.send_history_plot(args, ctx)
        else:
            await ctx.send("Invalid set of companies!")
    else:
        await ctx.send("Please enter atleast one company as argument.")


@bot.command(name="stock-history-bw-dates", help="Check historical plot of company(s) for start & end date.")
async def get_stock_history_in_date_interval(ctx, *args):
    if len(args) >= 3:
        await sub_bot.send_history_plot_in_date_interval(args, ctx)
    else:
        await ctx.send("Please enter correct usage")


@bot.command(name="create-channel", help="An admin creates a new channel.")
@commands.has_role('admin')
async def create_channel(ctx, channel_name):
    guild = ctx.guild
    existing_channel = discord.utils.get(guild.channels, name=channel_name)

    if not existing_channel:
        print(f'Creating a new channel- {channel_name}...')
        await guild.create_text_channel(channel_name)
        print('Channel created!')


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You do not have the correct role for this command.')
    elif isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send('Please enter correct usage.')


def create_msg(top_stock_company, top_stock_company_df):
    date = str(top_stock_company_df.head(1).index[0]).split(' ')[0]
    msg = '''\
        {company} EOF Data
        - Date: {Date}
        - Open: {Open}
        - High: {High}
        - Low: {Low}
        - Close: {Close}
        - Adj Close: {Adj_Close}
        - Volume: {Volume}\
     '''.format(company=top_stock_company, Date=date, Open=top_stock_company_df.iat[0, 0], High=top_stock_company_df.iat[0, 1], Low=top_stock_company_df.iat[0, 2], Close=top_stock_company_df.iat[0, 3], Adj_Close=top_stock_company_df.iat[0, 4], Volume=top_stock_company_df.iat[0, 5])

    return msg

@bot.command(name="current-stock-value", help="Check the current real-time stock value of a company.")
async def current_stock_value(ctx, stock_company):
    if stock_company in top_stock_companies:
        stock_data = yf.download(stock_company, period="1d", interval="1m")
        current_value = stock_data['Close'].iloc[-1]  # Get the latest closing price
        await ctx.send(f"The current real-time stock value of {stock_company} is: {current_value}")
    else:
        await ctx.send(f"Invalid stock company: {stock_company}")


@aiocron.crontab('0 7 * * mon-fri')
async def send_stock_details():

    top_stock_company = random.choice(top_stock_companies)
    top_stock_company_df = yf.download(top_stock_company, period="1d")

    msg = create_msg(top_stock_company, top_stock_company_df)

    existing_channel = discord.utils.get(
        bot.guilds[0].channels, name='stock-details')

    if not existing_channel:
        print(f'Creating a new channel- stock-details...')
        await bot.guilds[0].create_text_channel("stock-details")
        print('Channel created!')
        existing_channel = discord.utils.get(
            bot.guilds[0].channels, name='stock-details')

    await existing_channel.send(msg)
    await sub_bot.send_daily_trade_updates_plot(top_stock_company, existing_channel)


@aiocron.crontab('30 10-16 * * mon-fri')
async def show_hourly_plot():
    global df_not_none, count, df, random_company, nrows

    now = datetime.datetime.now()
    if now.hour == 10:
        df_not_none = True
        random_company = random.choice(top_stock_companies)
        df = yf.download(random_company,
                         period="1d", interval="1m")
        nrows = len(df.index)

    elif not df_not_none:
        df_not_none = True

        if count == 0:
            if now.hour == 11:
                count = 1
            elif now.hour == 12:
                count = 2
            elif now.hour == 13:
                count = 3
            elif now.hour == 14:
                count = 4
            elif now.hour == 15:
                count = 5
            else:
                count = 6

        random_company = random.choice(top_stock_companies)
        df = yf.download(random_company,
                         period="1d", interval="1m")
        nrows = len(df.index)

    limiter = 6.5 if (count == 6) else (count + 1)
    slice_limiter = 60*limiter

    if count == 6 and nrows != 390:
        slice_limiter = nrows

    df[60*count: slice_limiter].plot(y='Close', linewidth=0.85)

    plt.xlabel('Datetime')
    plt.ylabel('Close')
    plt.title('Stock prices of {company} for {hour1}:30 - {hour2}:30'.format(
        company=random_company, hour1=now.hour-1, hour2=now.hour))

    plt.savefig('images/stock_{i}.png'.format(i=count))

    existing_channel = discord.utils.get(
        bot.guilds[0].channels, name='stock-details')

    if not existing_channel:
        print(f'Creating a new channel- stock-details...')
        await bot.guilds[0].create_text_channel("stock-details")
        print('Channel created!')
        existing_channel = discord.utils.get(
            bot.guilds[0].channels, name='stock-details')

    await existing_channel.send(file=discord.File('images/stock_{i}.png'.format(i=count)))

    os.remove('images/stock_{i}.png'.format(i=count))

    count = count + 1

    if now.hour == 16:
        df_not_none = False
        count = 0

def get_stock_news(stock_symbol, num_articles=5):

    api_key = 'QzssxdGcdfoAa0wsoW7SFUjJStYDsEfpQQj2l8rr'
    
    base_url = f'https://finance.yahoo.com/_finance_doubledown/api/resource/news;searchTerm={stock_symbol}?bkt=%7B%22name%22%3A%22search%22%2C%22version%22%3A%221%22%7D&device=desktop&feature=canvass%2CnewContentAttribution%2CrelatedVideoFeatureFallback%2CvideoNativePlaylist%2CvideoNativePlaylistMpu&intl=us&lang=en-US&partner=none&prid=5vmlkfdtl1dpl'
    
    headers = {
        'Content-Type': 'application/json',
        'x-rapidapi-host': 'apidojo-yahoo-finance-v1.p.rapidapi.com',
        'x-rapidapi-key': api_key,
    }

    params = {
        'category': 'TOP',
        'count': num_articles,
    }

    try:
        response = requests.get(base_url, headers=headers, params=params)
        news_data = response.json()

        if 'items' in news_data:
            articles = news_data['items']['result']
            return articles
        else:
            return None

    except Exception as e:
        print(f"Error fetching news for {stock_symbol}: {e}")
        return None



bot.run('MTE2NDQ3NjAxOTQ1ODE4NzI4NA.G8M6s2.XAxo8_esrIQFjL796278gZ60rJQmCT3OwJ5oz4')
