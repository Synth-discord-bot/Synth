from os import getenv

from src import bot

if __name__ == "__main__":
    debug = False
    token = getenv("DISCORD_TOKEN", "token")
    
    bot.Bot(debug=debug).run(token)