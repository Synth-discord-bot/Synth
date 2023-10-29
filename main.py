from src import bot
from os import getenv

bot.Bot().run(getenv("DISCORD_TOKEN", "token"))
