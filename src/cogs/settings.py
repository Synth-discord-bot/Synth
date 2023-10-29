from typing import Dict

from disnake import Message, Embed
from disnake.ext import commands
# from disnake.ext.ipc import Server, ClientPayload

from src.utils import main_db


class Settings(commands.Cog):
    """Helper commands to set up the bot."""

    EMOJI = "⚙️"

    def __init__(self, bot) -> None:
        self.bot = bot
        self.settings_db = main_db

    async def cog_load(self) -> None:
        await self.settings_db.fetch_and_cache_all()

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
    #     if current_prefix == data.prefix:
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

    @commands.command()
    async def set_prefix(self, ctx: commands.Context, prefix: str) -> Message:
        """Set current prefix to another one"""
        if prefix is None or prefix == "":
            return await ctx.reply("Please enter a prefix!")
        elif len(prefix) >= 5:
            return await ctx.reply("Your prefix is too long!")
        else:
            await self.settings_db.set_prefix(ctx.guild.id, prefix)
            return await ctx.reply(f"Successfully set prefix to {prefix}")

    @commands.command()
    async def command_disable(self, ctx: commands.Context, command: str) -> Message:
        """Disable command for this guild (required administrator privileges)"""

        # first, try to get command from name
        command_name = ctx.bot.get_command(command)
        if command_name is None:
            # try to get command from alias
            for cmd in ctx.bot.commands:
                if command in cmd.aliases:
                    command_name = cmd
                    break

        if command_name and command_name != ctx.command:
            if isinstance(command_name, commands.Group):
                for command in command_name.commands:
                    await self.settings_db.add_command(
                        guild_id=ctx.guild.id, command=command.name
                    )
            await self.settings_db.add_command(
                guild_id=ctx.guild.id, command=command_name.name
            )
            return await ctx.reply(
                embed=Embed(
                    title="Information",
                    description=f"Successfully disabled command "
                    f"{'group' if isinstance(command_name, commands.Group) else ''} "
                    f"{command_name.name}",
                )
            )
        elif command_name == ctx.command:
            return await ctx.reply(
                embed=Embed(
                    title="Error", description=f"You can't disable this command"
                )
            )
        else:
            return await ctx.reply(
                embed=Embed(
                    title="Error", description=f"Could not find command {command}"
                )
            )


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Settings(bot=bot))
