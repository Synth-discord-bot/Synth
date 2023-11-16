from os import getenv

from src import bot

if __name__ == "__main__":
    token = getenv("DISCORD_TOKEN", "token")

    bot.Bot().run(token)
