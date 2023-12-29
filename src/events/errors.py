from datetime import datetime

import disnake
from disnake.ext import commands

from src.utils import main_db


class EventErrorHandler(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        super(EventErrorHandler, self).__init__()
        self.bot = bot
        self.settings_db = main_db

    @commands.Cog.listener()
    async def on_slash_command_error(
        self, inter: disnake.ApplicationCommandInteraction, error: commands.CommandError
    ) -> None:
        match error:
            case commands.errors.CommandOnCooldown:
                embed = disnake.Embed(
                    title="Cooldown",
                    description=f"Please wait {error.retry_after:.2f}s before using this command again.",
                    color=self.settings_db.get_embed_color(inter.guild.id),
                )
                await inter.response.send_message(embed=embed, delete_after=15)

            case commands.BadArgument:
                embed = disnake.Embed(
                    title="Bad Argument",
                    description=error,
                    color=self.settings_db.get_embed_color(inter.guild.id),
                )
                await inter.response.send_message(embed=embed, delete_after=15)

            case commands.MissingRequiredArgument:
                embed = disnake.Embed(
                    title="An argument missing",
                    description=f"Missing argument(s): {error.param.name}",
                    color=self.settings_db.get_embed_color(inter.guild.id),
                )
                await inter.response.send_message(embed=embed, delete_after=15)

            case commands.MissingPermissions:
                perms = [
                    f'- {perm.title().replace("_", " ").replace("Members", "")}\n'
                    for perm in error.missing_permissions
                ]
                embed = disnake.Embed(
                    title="Missing Permissions",
                    description=f"```diff\n{''.join(perms)}\n```",
                    color=self.settings_db.get_embed_color(inter.guild.id),
                )
                await inter.response.send_message(embed=embed, delete_after=15)

            case commands.BotMissingPermissions:
                perms = [
                    f'- {perm.title().replace("_", " ").replace("Members", "")}\n'
                    for perm in error.missing_permissions
                ]
                embed = disnake.Embed(
                    title="Synth is missing permissions",
                    description=f"```diff\n{''.join(perms)}\n```",
                    color=self.settings_db.get_embed_color(inter.guild.id),
                )
                await inter.response.send_message(embed=embed, delete_after=15)

            case commands.CheckFailure:
                pass
            case _:
                print(type(error), str(error))


def setup(bot: commands.Bot) -> None:
    bot.add_cog(EventErrorHandler(bot=bot))
