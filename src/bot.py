import logging
import os
import sys

import disnake
from disnake.ext import commands

# from disnake.ext.ipc import Server

from src.cogs.TicketsCog import SetupTicketSettings
from .utils import misc
from .utils.help import CustomHelpCommand
from .utils.misc import get_prefix, is_command_disabled


class Bot(commands.Bot):
    """The base class of Synth bot."""

    def __init__(self) -> None:
        super(Bot, self).__init__(
            help_command=CustomHelpCommand(),
            command_prefix=misc.bot_get_guild_prefix,
            intents=disnake.Intents.all(),
            reload=True,
            owner_ids=[419159175009009675, 999682446675161148, 1167458549132181668, ]
        )

        # self.ipc = Server(self, secret_key=config.SECRET_IPC_KEY)  # well... need talk about config
        self.i18n.load("src/utils/locale")

    def view_add(self):
        views = [SetupTicketSettings()]
        for view in views:
            self.add_view(view)
            logging.info(f"Loaded {view.id} view")

    async def on_message(self, message: disnake.Message):
        prefix = await get_prefix(message)

        if message.content.startswith(prefix):
            # TODO: blacklist

            # check if command is disabled
            command = message.content.split()[0][len(prefix) :]
            result = await is_command_disabled(message=message, command=command)
            if result:
                return

        return await self.process_commands(message=message)

    # async def setup_hook(self):
    #     await self.ipc.start()

    async def on_ready(self) -> None:
        logging.info(
            f"Invite link: https://discord.com/api/oauth2/authorize?client_id="
            f"{self.user.id}&permissions=980937982&scope=bot%20applications.commands"
        )
        logging.debug(f"Connected to {self.user}")
        for extension in os.listdir("src\\cogs"):
            if extension.endswith(".py"):
                try:
                    event_name = extension[:-3]
                    self.load_extension(f"src.cogs.{event_name}")
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

        for event in os.listdir("src\\events"):
            if not event.endswith(".py"):
                continue

            try:
                self.load_extension(f"src.events.{event[:-3]}")
            except (
                commands.ExtensionNotFound,
                commands.NoEntryPointError,
                commands.ExtensionFailed,
                commands.ExtensionError,
            ) as e:
                exc_type = e.__class__.__name__
                exc_line = sys.exc_info()[2].tb_lineno
                logging.error(
                    f"Failed to load {event}! {exc_type}: {str(e)}, line {exc_line}"
                )
                continue
            finally:
                logging.info(f"{event} event is loaded!")

        await self.wait_until_ready()
        await self.change_presence(
            activity=disnake.Activity(
                type=disnake.ActivityType.streaming,
                name="New multi-functional bot, Synth",
                state="Release soon...",
            )
        )
