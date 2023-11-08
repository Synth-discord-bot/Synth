from os import getenv

from src import bot

bot.Bot().run(getenv("DISCORD_TOKEN", "token"))
