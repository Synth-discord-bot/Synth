import logging

import disnake
from disnake.ext import commands
from .utils.misc import extension


# from disnake.ext.ipc import Server


class Bot(commands.InteractionBot):
    """The base class of Synth bot."""

    def __init__(self, debug: bool = False) -> None:
        super(Bot, self).__init__(
            # help_command=CustomHelpCommand(),
            # command_prefix=misc.bot_get_guild_prefix,
            intents=disnake.Intents.all(),
            reload=True,
            owner_ids=[419159175009009675, 999682446675161148, 1167458549132181668],
            test_guilds=[1109511263509291098]#, 1175423496088735857],
        )

        # self.ipc = Server(self, secret_key=config.SECRET_IPC_KEY)  # well... need talk about config
        self.i18n.load("src/utils/locale")
        self.debug = debug

    # async def on_message(self, message: disnake.Message):
    #     prefix = await get_prefix(message)
    #     prefix_len = len(prefix)

    #     if message.content.startswith(prefix):
    #         # TODO: blacklist

    #         # check if command is disabled
    #         command = message.content.split()[0][prefix_len:]
    #         result = await is_command_disabled(message=message, command=command)
    #         if result:
    #             return

    #     return await self.process_commands(message=message)

    # async def setup_hook(self):
    #     await self.ipc.start()

    async def on_ready(self) -> None:
        logging.info(
            f"Invite link: https://discord.com/api/oauth2/authorize?client_id="
            f"{self.user.id}&permissions=980937982&scope=bot%20applications.commands"
        )
        logging.debug(f"Connected to {self.user}")

        await extension(self)
        await self.wait_until_ready()
        await self.change_presence(
            activity=disnake.Activity(
                type=disnake.ActivityType.competing,
                name=f"/help | v1.0",
                status=disnake.Status.idle,
            )
        )
