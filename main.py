from src import bot
from os import getenv

bot = bot.Bot()

bot.run(getenv("DISCORD_TOKEN", "token"))
