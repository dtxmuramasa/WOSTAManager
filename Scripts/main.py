import os
from dotenv import load_dotenv
from os.path import join, dirname

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
_DISCORD_TOKEN_ = os.environ.get('DISCORD_TOKEN')


import discord
intents = discord.Intents.default()
intents.members = True
intents.message_content = True


## Logging
import logging
import logging.handlers
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
logging.getLogger('discord.http').setLevel(logging.INFO)

logHandler = logging.handlers.RotatingFileHandler(
        filename='log/discord.log',
        encoding='utf-8',
        mode='w',
        maxBytes=32 * 1024 * 1024, # 32MB
        backupCount=5
    )
dt_fmt = '%Y-%m-%d %H:%M:%S'
logFormatter = logging.Formatter(
    '[{asctime}] [{levelname:<8}] {name}: {message}',
    style='{',
    datefmt=dt_fmt
)
logHandler.setFormatter(logFormatter)
logger.addHandler(logHandler)


## Database
from Models import TADB
tadb = TADB.TADatabase(logger)


## Bot
import discord
from discord.ext import commands
bot = commands.Bot(command_prefix='!', intents=intents)

from BotCogs import TAManager
from BotCogs import CrazyDice
from BotCogs import Omikuji
from BotCogs import VCSupport
@bot.event
async def setup_hook():
    await bot.add_cog(TAManager.TAManagerCog(bot, tadb, logger))
    await bot.add_cog(CrazyDice.CrazyDiceCog(bot, logger))
    await bot.add_cog(VCSupport.VCSupportCog(bot, logger))
    await bot.add_cog(Omikuji.OmikujiCog(bot, logger))
    await bot.tree.sync()

@bot.event
async def on_ready():
    logger.info(f'Logged in as {bot.user.name} ({bot.user.id})')

bot.run(_DISCORD_TOKEN_)
