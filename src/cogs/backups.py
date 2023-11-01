import asyncio
import base64
import os
from io import BytesIO

import disnake
import ujson
from disnake.ext import commands
from disnake.utils import get

from src.utils import backups
from src.utils.backup import Backup as BackupGuild
from src.utils.misc import is_owner, has_bot_permissions


class Backup(commands.Cog):
    """Backup commands"""
    EMOJI = "📅"

    def __init__(self, bot: commands.Bot) -> None:
        super(Backup, self).__init__()
        self.bot = bot
        self.backups = backups

    async def cog_load(self) -> None:
        await self.backups.fetch_and_cache_all()

    @commands.group(invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def backup(self, ctx: commands.Context) -> None:
        if ctx.invoked_subcommand is None:
            embed = disnake.Embed(
                title="<:backup:1168599276520226826> Backup commands",
                color=0x2F3136,
                description=(
                    f"`{ctx.prefix}backup create` – Create/update backup\n"
                    f"`{ctx.prefix}backup delete` – Delete backup\n"
                    f"`{ctx.prefix}backup load` – Load backup\n"
                    f"`{ctx.prefix}backup file` – JSON file of server backup"
                ),
            )

            if backups.check_backup(ctx.guild):
                data = await backups.get(guild_id=ctx.guild.id)
                data = data["backup_data"]
                embed.add_field(
                    name="Last Backup:",
                    value=f"<t:{data['info']['created']}:f> (<t:{data['info']['created']}:R>)",
                )

            await ctx.send(embed=embed)

    @backup.command()
    @commands.cooldown(1, 5, commands.BucketType.guild)
    @is_owner()
    async def create(self, ctx: commands.Context) -> None:
        global msg
        embed = disnake.Embed(color=0x2F3136)
        try:
            embed.title = "<a:loading:1168599537682755584> Please wait..."
            embed.description = "Creating a server backup..."
            msg = await ctx.send(embed=embed)

            backup_data = await BackupGuild(ctx.guild).create()

            await self.backups.update_backups_info(ctx.guild.id, backup_data)

            embed.colour = 0x2F3136
            embed.title = "Finished"
            embed.description = "Server backup has been successfully created"
            await msg.edit(embed=embed)

        except (Exception, ExceptionGroup) as e:
            # raise e
            # exc_type = e.__class__.__name__
            # exc_line = sys.exc_info()[2].tb_lineno
            # logging.error(f"[log]! {exc_type}: {str(e)}, line {exc_line}")
            embed.colour = 0x2F3136
            embed.title = "An error occurred"
            embed.description = (
                "An error occurred when trying to save the server."
            )
            await msg.edit(embed=embed)

    @backup.command()
    @commands.cooldown(1, 5, commands.BucketType.guild)
    @is_owner()
    @has_bot_permissions()
    async def load(self, ctx: commands.Context) -> None:
        embed = disnake.Embed(color=0x2F3136)
        data = await self.backups.get(ctx.guild.id, to_return="backup_data")

        if not data:
            embed.title = "An error occurred"
            embed.description = "There is no backup for this server"
            await ctx.send(embed=embed)
            return

        embed.title = "<a:loading:1168599537682755584> Loading Backup"
        embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar)

        msg = await ctx.send(embed=embed)

        embed.description = "<:information:1168237956591530065> Stage 1 of 6\n> **Deleting channels**"
        await msg.edit(embed=embed)

        for channel in ctx.guild.channels:
            try:
                if channel != ctx.channel:
                    await channel.delete()
            except (disnake.Forbidden, disnake.NotFound, disnake.HTTPException):
                continue

        embed.description = "<:information:1168237956591530065> Stage 2 of 6\n> **Deleting roles**"
        await msg.edit(embed=embed)

        for role in ctx.guild.roles:
            try:
                await role.delete()
            except (disnake.Forbidden, disnake.HTTPException):
                continue

        embed.description = "<:information:1168237956591530065> Stage 3 of 6\n> **Creating roles**"
        await msg.edit(embed=embed)

        roles = data["roles"]
        for k in range(len(roles) + 1):
            try:
                await ctx.guild.create_role(
                    name=data["roles"][str(k)]["name"],
                    colour=disnake.Colour(value=data["roles"][str(k)]["color"]),
                    permissions=disnake.Permissions(
                        permissions=data["roles"][str(k)]["perms"]
                    ),
                    hoist=data["roles"][str(k)]["hoist"],
                    mentionable=data["roles"][str(k)]["mentionable"],
                )
            except (
                    disnake.NotFound,
                    disnake.Forbidden,
                    disnake.HTTPException,
                    TypeError,
                    KeyError,
            ):
                continue

        embed.description = "<:information:1168237956591530065> Stage 4 of 6\n> **Creating categories**"
        await msg.edit(embed=embed)

        categories = data["category"]
        for i in range(len(categories) + 1):
            try:
                overwrites = {}
                if data["category"].get(str(i), None) is not None:
                    raw_overwrites = data["category"][str(i)]["perms"]

                    for role_to_recovery in ctx.guild.roles:
                        try:
                            ovw = disnake.PermissionOverwrite.from_pair(
                                disnake.Permissions(
                                    permissions=raw_overwrites[role_to_recovery.name][
                                        "a"
                                    ]
                                ),
                                disnake.Permissions(
                                    permissions=raw_overwrites[role_to_recovery.name][
                                        "d"
                                    ]
                                ),
                            )
                            overwrites[role_to_recovery] = ovw
                        except (Exception, ExceptionGroup):
                            continue

                    await ctx.guild.create_category(
                        name=data["category"][str(i)]["name"],
                        position=data["category"][str(i)]["position"],
                        overwrites=overwrites,
                    )
            except (disnake.Forbidden, disnake.HTTPException, TypeError):
                continue

        embed.description = "<:information:1168237956591530065> Stage 5 of 6\n> **Creating channels**"
        await msg.edit(embed=embed)

        text_channels = data["text"]
        for i in range(len(text_channels) + 1):
            try:
                overwrites = {}
                if data["text"].get(str(i), None) is not None:
                    raw_overwrites = data["text"][str(i)]["perms"]

                    for old_role_permissions in ctx.guild.roles:
                        try:
                            ovw = disnake.PermissionOverwrite.from_pair(
                                disnake.Permissions(
                                    permissions=raw_overwrites[
                                        old_role_permissions.name
                                    ]["a"]
                                ),
                                disnake.Permissions(
                                    permissions=raw_overwrites[
                                        old_role_permissions.name
                                    ]["d"]
                                ),
                            )
                            overwrites[old_role_permissions] = ovw
                        except (Exception, ExceptionGroup):
                            continue

                    new_channel_name = data["text"][str(i)]["name"]
                    current_channel_name = ctx.channel.name

                    if new_channel_name != current_channel_name:
                        if data["text"][str(i)].get("category", None) is None:
                            await ctx.guild.create_text_channel(
                                name=new_channel_name,
                                topic=data["text"][str(i)]["topic"],
                                nsfw=data["text"][str(i)]["nsfw"],
                                slowmode_delay=data["text"][str(i)]["slowmode"],
                                position=data["text"][str(i)]["position"],
                                overwrites=overwrites,
                            )
                        else:
                            await ctx.guild.create_text_channel(
                                name=new_channel_name,
                                topic=data["text"][str(i)]["topic"],
                                nsfw=data["text"][str(i)]["nsfw"],
                                slowmode_delay=data["text"][str(i)]["slowmode"],
                                position=data["text"][str(i)]["position"],
                                category=get(
                                    ctx.guild.categories,
                                    name=data["text"][str(i)]["category"],
                                ),
                                overwrites=overwrites,
                            )
            except (disnake.Forbidden, disnake.HTTPException, TypeError):
                continue

        voice_channels = data["voice"]
        for i in range(len(voice_channels) + 1):
            try:
                overwrites = {}
                if data["voice"].get(str(i), None) is not None:
                    raw_overwrites = data["voice"][str(i)]["perms"]

                    for old_role_permissions in ctx.guild.roles:
                        try:
                            ovw = disnake.PermissionOverwrite.from_pair(
                                disnake.Permissions(
                                    permissions=raw_overwrites[
                                        old_role_permissions.name
                                    ]["a"]
                                ),
                                disnake.Permissions(
                                    permissions=raw_overwrites[
                                        old_role_permissions.name
                                    ]["d"]
                                ),
                            )
                            overwrites[old_role_permissions] = ovw
                        except (Exception, ExceptionGroup):
                            continue

                    if data["voice"][str(i)].get("category", None) is None:
                        await ctx.guild.create_voice_channel(
                            name=data["voice"][str(i)]["name"],
                            user_limit=data["voice"][str(i)]["limit"],
                            bitrate=data["voice"][str(i)]["bitrate"],
                            position=data["voice"][str(i)]["position"],
                            overwrites=overwrites,
                        )
                    else:
                        await ctx.guild.create_voice_channel(
                            name=data["voice"][str(i)]["name"],
                            user_limit=data["voice"][str(i)]["limit"],
                            bitrate=data["voice"][str(i)]["bitrate"],
                            position=data["voice"][str(i)]["position"],
                            category=get(  # TODO: FIX
                                ctx.guild.categories,
                                name=data["voice"][str(i)]["category"],
                            ),
                            overwrites=overwrites,
                        )
            except (disnake.Forbidden, disnake.HTTPException, TypeError):
                continue

        embed.description = "<:information:1168237956591530065> Stage 6 of 6\n> **Restoring the server main information**"
        await msg.edit(embed=embed)

        """
         "guild": {
                "name": self.guild.name,
                "rules_channel": self.guild.rules_channel.name
                if self.guild.rules_channel
                else None,
                "public_updates_channel": self.guild.public_updates_channel.name
                if self.guild.public_updates_channel
                else None,
                "afk_channel": self.guild.afk_channel.name
                if self.guild.afk_channel
                else None,
                "afk_timeout": self.guild.afk_timeout if self.guild.afk_timeout else 0,
                "description": self.guild.description,
            },
        """

        icon_data = None
        if data["guild"]["icon"]:
            icon_data = BytesIO(base64.b64decode(data["guild"]["icon"]))

        banner_data = None
        if data["guild"]["banner"]:
            banner_data = BytesIO(base64.b64decode(data["guild"]["banner"]))

        verification_level_mapping = {
            "none": disnake.VerificationLevel.none,
            "low": disnake.VerificationLevel.low,
            "medium": disnake.VerificationLevel.medium,
            "high": disnake.VerificationLevel.high,
            "highest": disnake.VerificationLevel.highest,
        }

        # Get the verification level from MongoDB and convert it
        ver_level_mongo = data["guild"]["verification_level"][0]
        # Assuming the first element in the list represents the verification level
        ver_level = verification_level_mapping.get(ver_level_mongo, disnake.VerificationLevel.none)

        afk_channel = disnake.utils.get(ctx.guild.voice_channels, name=data["guild"]["afk_channel"])
        system_channel = disnake.utils.get(ctx.guild.text_channels, name=data["guild"]["system_channel"])
        rules_channel = disnake.utils.get(ctx.guild.text_channels, name=data["guild"]["rules_channel"])

        await ctx.guild.edit(
            name=data["guild"]["name"],
            afk_timeout=data["guild"]["afk_timeout"],
            description=data["guild"]["description"],
            rules_channel=rules_channel or None,
            public_updates_channel=data["guild"]["public_updates_channel"] or None,
            premium_progress_bar_enabled=data["guild"]["premium_progress_bar_enabled"],
            system_channel=system_channel,
            afk_channel=afk_channel,
            verification_level=ver_level,
            icon=icon_data.read() if icon_data is not None else None,
            banner=banner_data.read() if banner_data is not None else None,
        )

        await asyncio.sleep(3)

        embed.title = "<a:success:1168599845192339577> Success"
        embed.colour = 0x2F3136
        embed.description = "Server backup has been successfully loaded."

        await msg.edit(embed=embed)

    @backup.command()
    @commands.cooldown(1, 50, commands.BucketType.guild)
    @commands.has_permissions(administrator=True)
    async def file(self, ctx: commands.Context) -> None:
        if backups.check_backup(ctx.guild):
            backup = {
                "guild": {},
                "text_channels": {},
                "voice_channels": {},
                "categories": {},
                "roles": {},
            }
            data = await self.backups.get(ctx.guild.id, to_return="backup_data")

            backup["guild"]["name"] = data["guild"]["name"]
            backup["guild"]["afk_timeout"] = data["guild"]["afk_timeout"]
            backup["guild"]["description"] = data["guild"]["description"]
            backup["text_channels"] = data["text"]
            backup["voice_channels"] = data["voice"]
            backup["categories"] = data["category"]
            backup["roles"] = data["roles"]

            with open(f"{str(ctx.guild.id)}.json", "w") as f:
                ujson.dump(backup, f, indent=4)

            await ctx.send(
                file=disnake.File(f"{str(ctx.guild.id)}.json")
            )
            os.remove(f"{str(ctx.guild.id)}.json")
        else:
            embed = disnake.Embed(
                colour=0x2F3136,
                title="An error occurred",
                description="There isn't any backup created for this server",
            )

            await ctx.send(embed=embed)

    @backup.command()
    @is_owner()
    async def delete(self, ctx: commands.Context) -> None:
        embed = disnake.Embed(color=0x2F3136)

        if backups.check_backup(ctx.guild):
            await self.backups.remove_from_db({"_id": ctx.guild.id})
            embed.title = "Finished"
            embed.description = "Server backup has been successfully deleted"
            await ctx.send(embed=embed)
        else:
            embed.title = "An error occurred"
            embed.description = "Server backup hasn't been deleted."
            embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar)
            await ctx.send(embed=embed)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Backup(bot))
