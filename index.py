from helpers import bot_config
from helpers import logger

from discord.ext import commands
import os


config = bot_config.load()


bot = commands.Bot(command_prefix=config['prefix'])
bot.remove_command('help')


for file in os.listdir('cogs'):
    if file.endswith('.py'):
        name = file[:-3]
        bot.load_extension(f'cogs.{name}')


@bot.event
async def on_ready():
    print('Ready.')
    logger.log(f'Logged in as "{bot.user}"')


bot.run(config['token'])