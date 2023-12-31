import disnake
from disnake.ext import commands
from traceback import format_exception
import contextlib
import io
import textwrap


class Developers(commands.Cog):
    def __init__(self, bot: commands.Bot):
        super(Developers, self).__init__()
        self.bot = bot

    # TODO: EVAL WITHOUGHT INTERNET
    # TODO: BLACKLIST SETTINGS
    # TODO: COGS LOAD/UNLOAD/RELOAD


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Developers(bot))
