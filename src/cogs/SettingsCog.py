import disnake
from disnake.ext import commands
from disnake.interactions import MessageInteraction
from typing import Dict, List, Optional

from src.utils import main_db, commands_db
from src.utils.settingsviews import (
    CommandsContextCommands,
    CommandsSlashCommands,
    CommandsSlashSettings,
    EmbedColorSettings,
    LanguageSettings,
    PrefixSettings,
    CommandsSettings,
)


class SettingsView(disnake.ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.bot = bot
        self.settings_db = main_db
        self.commands_db = commands_db

    @disnake.ui.string_select(
        cls=disnake.ui.StringSelect,  # type: ignore
        options=[
            disnake.SelectOption(label="Language", value="language", emoji="🌍"),
            disnake.SelectOption(label="Prefix", value="prefix", emoji="✏️"),
            disnake.SelectOption(label="Commands", value="commands", emoji="⌨️"),
            disnake.SelectOption(label="Embed color", value="embed_color", emoji="🎨"),
        ],
    )
    async def select_callback(
        self, select: disnake.ui.StringSelect, interaction: MessageInteraction
    ):
        if select.values[0] == "language":
            await interaction.send(
                f"Current language: ...",
                ephemeral=True,
                view=LanguageSettings(self.bot),
            )
        elif select.values[0] == "prefix":
            prefix = await self.settings_db.get_prefix(interaction.guild.id)
            await interaction.send(
                f"Current prefix: `{prefix}`",
                ephemeral=True,
                view=PrefixSettings(self.bot),
            )
        elif select.values[0] == "commands":
            await interaction.send(
                "There is you can disable commands",
                ephemeral=True,
                view=CommandsSettings(self.bot),
            )
        elif select.values[0] == "embed_color":
            color = await self.settings_db.get_embed_color(interaction.guild.id)
            await interaction.send(
                f"Current embed color: `{color}`",
                ephemeral=True,
                view=EmbedColorSettings(self.bot),
            )


class Settings(commands.Cog):
    """Commands to fully customize the bot."""

    EMOJI = "<:settings:1169685352114552922>️"

    def __init__(self, bot) -> None:
        self.bot = bot
        self.settings_db = main_db
        self.command_db = commands_db

    async def cog_load(self) -> None:
        await self.settings_db.fetch_and_cache_all()
        await self.command_db.fetch_and_cache_all()

    @commands.slash_command(name="settings", description="Get or set the bot's prefix")
    async def settings(self, interaction):
        await interaction.send(
            "Choice a module", view=SettingsView(self.bot), ephemeral=True
        )

    @staticmethod
    def custom_cooldown(message: disnake.Message):
        prefix = main_db.get_prefix_from_cache(message.guild.id)
        len_prefix = len(prefix)

        if message.content.startswith(prefix):
            command = message.content.split()[0][len_prefix:]

            if cooldown := commands_db.get_command_cooldown(message.guild.id, command):
                return commands.Cooldown(1, cooldown)

        # return commands.Cooldown(1, 5)

        # role = disnake.utils.get(message.guild.roles, id=999682446675161148)
        # if role in message.author.roles:
        #     return commands.Cooldown(1, 5)
        # elif message.author.id in [123, 1234, 12345, 123456]:
        #     return commands.Cooldown(1, 1)
        # else:
        #     if command == "dmcheck":
        #         return commands.Cooldown(1, 30)
        #     elif command == "help":
        #         return commands.Cooldown(1, 15)
        #     elif command == "ping":
        #         return commands.Cooldown(1, 20)
        #     elif command == "spam":
        #         return commands.Cooldown(1, 30)
        #     elif command == "spam_custom":
        #         return commands.Cooldown(1, 30)
        #     elif command == "join_spam":
        #         return commands.Cooldown(1, 30)
        #     else:
        #         return commands.Cooldown(1, 15)

    # @commands.check(CustomCooldown(1, 300, 1, 0, commands.BucketT., elements=[999682446675161148]))
    # @commands.dynamic_cooldown(custom_cooldown, commands.BucketType.user)
    # @commands.command()
    # async def test(self, ctx: commands.Context):
    #     # await self.command_db.set_cooldown(ctx.guild.id, ctx.command.name, 10)
    #     await ctx.send(await self.command_db.get_cooldown(ctx.message))

    # @Server.route()
    # async def get_prefix(self, data: ClientPayload) -> Dict[str, str]:
    #     prefix = await self.settings_db.get_prefix(data.guild_id)
    #
    #     return {
    #         "message": f"Current prefix is {prefix}",
    #         "prefix": prefix,
    #         "status": "OK",
    #     }
    #
    # @Server.route()
    # async def set_prefix(self, data: ClientPayload) -> Dict[str, str]:
    #     current_prefix = await self.settings_db.get_prefix(data.guild_id)
    #
    #     if current_prefix == data.prefix: z>>test

    #         return {
    #             "message": f"Prefix already set to {data.prefix}",
    #             "prefix": current_prefix,
    #             "status": "ALREADY_IN_DB",
    #         }
    #
    #     await self.settings_db.set_prefix(data.guild_id, data.prefix)
    #     return {
    #         "message": f"Successfully set prefix to {data.prefix}",
    #         "prefix": data.prefix,
    #         "status": "OK",
    #     }

    # @commands.command()
    # async def set_prefix(self, ctx: commands.Context, prefix: str) -> disnake.Message:
    #     """Set the current prefix to another one"""
    #     if prefix is None or prefix == "":
    #         return await ctx.reply("Please enter a prefix!")
    #     elif len(prefix) >= 5:
    #         return await ctx.reply("Your prefix is too long!")
    #     else:
    #         await self.settings_db.set_prefix(ctx.guild.id, prefix)
    #         return await ctx.reply(f"Successfully set prefix to {prefix}")

    # @commands.command()
    # async def command_disable(
    #     self, ctx: commands.Context, command: str
    # ) -> disnake.Message:
    #     """Disable command for this guild (required administrator privileges)"""

    #     # first, try to get command from name
    #     command_name = ctx.bot.get_command(command)
    #     if command_name is None:
    #         # try to get command from alias
    #         for cmd in ctx.bot.commands:
    #             if command in cmd.aliases:
    #                 command_name = cmd
    #                 break

    #     if command_name and command_name != ctx.command:
    #         if isinstance(command_name, commands.Group):
    #             for command in command_name.commands:
    #                 await self.settings_db.add_command(
    #                     guild_id=ctx.guild.id, command=command.name
    #                 )
    #         await self.settings_db.add_command(
    #             guild_id=ctx.guild.id, command=command_name.name
    #         )
    #         return await ctx.reply(
    #             embed=disnake.Embed(
    #                 title="Information",
    #                 description=f"Successfully disabled command "
    #                 f"{'group' if isinstance(command_name, commands.Group) else ''} "
    #                 f"{command_name.name}",
    #             )
    #         )
    #     elif command_name == ctx.command:
    #         return await ctx.reply(
    #             embed=disnake.Embed(
    #                 title="Error", description=f"You can't disable this command"
    #             )
    #         )
    #     else:
    #         return await ctx.reply(
    #             embed=disnake.Embed(
    #                 title="Error", description=f"Could not find command {command}"
    #             )
    #         )


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Settings(bot=bot))
