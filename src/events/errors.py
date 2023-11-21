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
        print(type(error))
        if isinstance(error, commands.errors.CommandOnCooldown):
            embed = disnake.Embed(
                title="Cooldown",
                description=f"Please wait {error.retry_after:.2f}s before using this command again.",
                color=self.settings_db.get_embed_color(inter.guild.id),
            )
            await inter.response.send_message(embed=embed, delete_after=15)
        elif isinstance(error, commands.BadArgument):
            embed = disnake.Embed(
                title="Bad Argument",
                description=error,
                color=self.settings_db.get_embed_color(inter.guild.id),
            )
            await inter.response.send_message(embed=embed, delete_after=15)
        elif isinstance(error, commands.MissingRequiredArgument):
            embed = disnake.Embed(
                title="An argument missing",
                description=f"Missing argument(s): {error.param.name}",
                color=self.settings_db.get_embed_color(inter.guild.id),
            )
            await inter.response.send_message(embed=embed, delete_after=15)
        elif isinstance(error, commands.MissingPermissions):
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
        elif isinstance(error, commands.errors.BotMissingPermissions):
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
        elif isinstance(error, commands.CheckFailure):
            pass

    @commands.Cog.listener()
    async def on_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        # print(type(error))
        if isinstance(error, commands.errors.CommandOnCooldown):
            embed = disnake.Embed(
                title="Cooldown",
                description=f"Please wait {error.retry_after:.2f}s before using this command again.",
                color=0xFF0000,
            )
            await ctx.send(embed=embed, delete_after=15)
        elif isinstance(error, commands.BadArgument):
            embed = disnake.Embed(
                title="Bad Argument", description=error, color=0xFF0000
            )
            await ctx.send(embed=embed, delete_after=15)
        elif isinstance(error, commands.MissingRequiredArgument):
            embed = disnake.Embed(
                title="An argument missing",
                description=f"Missing argument(s): {error.param.name}",
                color=0xFF0000,
            )
            await ctx.send(embed=embed, delete_after=15)
        elif isinstance(error, commands.MissingPermissions):
            perms = [
                f'- {perm.title().replace("_", " ").replace("Members", "")}\n'
                for perm in error.missing_permissions
            ]
            embed = disnake.Embed(
                title="Missing Permissions",
                description=f"```diff\n{''.join(perms)}\n```",
                color=0xFF0000,
            )
            await ctx.send(embed=embed, delete_after=15)
        elif isinstance(error, commands.errors.BotMissingPermissions):
            perms = [
                f'- {perm.title().replace("_", " ").replace("Members", "")}\n'
                for perm in error.missing_permissions
            ]
            embed = disnake.Embed(
                title="Synth is missing permissions",
                description=f"```diff\n{''.join(perms)}\n```",
                color=0xFF0000,
            )
            await ctx.send(embed=embed, delete_after=15)
        elif isinstance(error, commands.CheckFailure):
            pass
        # elif isinstance(error, commands.errors.CommandInvokeError): embed = disnake.Embed( title="Cooldown",
        # description=f"Please wait {error.retry_after:.2f}s before using this command again.", color=0xFF0000,
        # ) await ctx.send(embed=embed, delete_after=15) else: embed = disnake.Embed( title="Error", description="We
        # apologise for the inconvenience, but an ctxnal error has occurred during the runtime. Please contact Synth
        # support and provide the error ID for further assistance.", color=0xFF0000, timestamp=datetime.now(),
        # ) embed.set_footer(text="Error ID: ...") url_button = disnake.ui.Button( label="Support Server",
        # url="https://discord.gg/7vT3H3tVYp", emoji="<:synth:1173688715529420850>", ) await ctx.author.send(
        # zembed=embed, components=[disnake.ui.ActionRow(url_button)] )


def setup(bot: commands.Bot) -> None:
    bot.add_cog(EventErrorHandler(bot=bot))
