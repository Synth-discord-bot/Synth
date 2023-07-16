import sys

import disnake
from disnake.ext import commands
import logging
import os
from . import testdb


class Bot(commands.Bot):
    def __init__(self) -> None:
        super(Bot, self).__init__(
            help_command=None,
            command_prefix=[">>", ">"],
            intents=disnake.Intents.all(),
            reload=True,
        )

    async def on_connect(self):
        await testdb.fetch_and_cache_all()

    async def on_ready(self) -> None:
        logging.debug(f"Connected to {self.user}")
        for directory in os.listdir("src\\cogs"):
            if directory.endswith(".py"):
                try:
                    self.load_extension(f"src.cogs.{directory[:-3]}")
                    logging.debug(directory)
                except (
                    commands.ExtensionNotFound,
                    commands.NoEntryPointError,
                    commands.ExtensionFailed,
                    commands.ExtensionError,
                ) as e:
                    _, __, exc_tb = sys.exc_info()
                    logging.error(
                        f"Failed to load {directory}! {e.__class__.__name__}: {str(e)}, line {exc_tb.tb_lineno}"
                    )
                    continue
                except commands.ExtensionAlreadyLoaded:
                    continue
