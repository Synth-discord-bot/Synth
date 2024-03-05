from os import getenv

from src import bot

if __name__ == "__main__":
    debug = bool(getenv("DEBUG", False))

    bot.Bot(debug=debug).run(getenv("TOKEN"))
