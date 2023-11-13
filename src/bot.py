import logging
import os
import traceback

import disnake
from disnake.ext import commands

from .utils import misc
from .utils.help import CustomHelpCommand
from .utils.misc import get_prefix, is_command_disabled


# from disnake.ext.ipc import Server


class Bot(commands.Bot):
    """The base class of Synth bot."""

    def __init__(self, debug: bool) -> None:
        super(Bot, self).__init__(
            help_command=CustomHelpCommand(),
            command_prefix=misc.bot_get_guild_prefix,
            intents=disnake.Intents.all(),
            reload=True,
            owner_ids={419159175009009675, 999682446675161148, 1167458549132181668},
        )
        self.debug = debug

        # self.ipc = Server(self, secret_key=config.SECRET_IPC_KEY)  # well... need talk about config
        self.i18n.load("src/utils/locale")

    async def on_message(self, message: disnake.Message) -> None:
        prefix = await get_prefix(message)
        prefix_len = len(prefix)

        if message.content.startswith(prefix):
            # TODO: blacklist

            # check if command is disabled
            command = message.content.split()[0][prefix_len:]
            if self.debug:
                logging.debug(f"{message.author} has executed the command {command}")
            result = await is_command_disabled(message=message, command=command)
            if result:
                return

        return await self.process_commands(message=message)

    async def on_ready(self) -> None:
        if self.debug:
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
                    logging.error(
                        f"\n\nFailed to load {extension}!\n{traceback.print_exception(e)}"
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
                logging.error(
                    f"Failed to load {event}!\n{traceback.print_exception(e)}"
                )
                continue
            finally:
                logging.info(f"{event} event is loaded!")

        await self.wait_until_ready()
        await self.change_presence(
            activity=disnake.Activity(
                type=disnake.ActivityType.competing,
                name=f">>help | v1.0.",
                status=disnake.Status.idle,
            )
        )
