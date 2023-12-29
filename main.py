from os import getenv

from src import bot

if __name__ == "__main__":
    debug = bool(getenv("DEBUG", False))
    token = "MTE2ODIyNjg5NTc1ODkwMTQwOA.GCNd9-.Qgk_m-7atWUxb73e4LMmB564bUyPP8w0xlmTX4"

    bot.Bot(debug=debug).run(token)
