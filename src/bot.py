import logging
import os
import sys

import disnake
from disnake.ext import commands
from disnake_ipc.ext.ipc import Server

from bot_site import config
from .utils import misc


class Bot(commands.Bot):
    """The base class of Synth bot."""

    def __init__(self) -> None:
        super(Bot, self).__init__(
            help_command=None,
            command_prefix=misc.get_guild_prefix,
            intents=disnake.Intents.all(),
            reload=True,
        )

        self.ipc = Server(self, secret_key=config.SECRET_IPC_KEY)

    async def setup_hook(self):
        await self.ipc.start()

    async def on_ready(self) -> None:
        logging.debug(f"Connected to {self.user}")
        cogs_directory = "src\\cogs"
        for extension in os.listdir(cogs_directory):
            if extension.endswith(".py"):
                try:
                    cog_name = extension[:-3]
                    cog_path = f"src.cogs.{cog_name}"
                    self.load_extension(cog_path)
                except (
                        commands.ExtensionNotFound,
                        commands.NoEntryPointError,
                        commands.ExtensionFailed,
                        commands.ExtensionError,
                ) as e:
                    exc_type = e.__class__.__name__
                    exc_line = sys.exc_info()[2].tb_lineno
                    logging.error(
                        f"Failed to load {extension}! {exc_type}: {str(e)}, line {exc_line}"
                    )
                    continue
                finally:
                    logging.info(f"{extension} is loaded!")
