from os import getenv

from src import bot

if __name__ == "__main__":
    debug = True if getenv("DEBUG", False) == "true" else False
    token = getenv("DISCORD_TOKEN", "token")

    bot.Bot().run(token)
