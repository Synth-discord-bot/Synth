import json
import os
import time

import disnake
from disnake.ext import commands
from disnake.utils import get

from src.utils import backups


class Backup(commands.Cog):
    def __init__(self, bot: commands.Bot):
        super(Backup, self).__init__()
        self.bot = bot

    @commands.group(invoke_without_command=True)
    @commands.cooldown(1, 5, commands.BucketType.guild)
    @commands.has_permissions(administrator=True)
    async def backup(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            prefix = ctx.prefix
            embed = disnake.Embed(color=0x43ADF3)
            embed.title = "Backup Commands"
            embed.description = (
                f"`{prefix}backup create` – Create/update backup\n"
                f"`{prefix}backup delete` – Delete backup\n"
                f"`{prefix}backup load` – Load backup"
            )
            if backups.check_backup(ctx.guild):
                data = backups.get(ctx.guild.id, {"info": True})
                embed.add_field(
                    name="Last Backup:",
                    value=f"<t:{data['info']['created']}:f> (<t:{data['info']['created']}:R>)",
                )
            await ctx.send(embed=embed)

    @backup.command()
    async def create(self, ctx: commands.Context):
        embed = disnake.Embed(color=0x43ADF3)
        if ctx.author == ctx.guild.owner:
            try:
                embed.title = "Please wait..."
                embed.description = "Creating a server backup..."
                msg = await ctx.send(embed=embed)

                backup_data = {
                    "info": {
                        "nextsave": 2147483647,
                        "interval": 0,
                        "created": int(time.time()),
                    },
                    "guild": {"name": ctx.guild.name},
                    "text": {},
                    "voice": {},
                    "category": {},
                    "roles": {},
                }

                text_channel_index = 0
                for text_channel in ctx.guild.text_channels:
                    text_channel_data = {
                        "name": text_channel.name,
                        "topic": text_channel.topic.replace(".", "")
                        if text_channel.topic
                        else None,
                        "slowmode": text_channel.slowmode_delay,
                        "nsfw": text_channel.nsfw,
                        "position": text_channel.position,
                        "perms": {
                            role.name: {"a": ovw[0].value, "d": ovw[1].value}
                            for role, ovw in text_channel.overwrites.items()
                        },
                    }
                    if text_channel.category is not None:
                        text_channel_data["category"] = text_channel.category.name
                    backup_data["text"][str(text_channel_index)] = text_channel_data
                    text_channel_index += 1

                voice_channel_index = 0
                for voice_channel in ctx.guild.voice_channels:
                    voice_channel_data = {
                        "name": voice_channel.name.replace(".", " "),
                        "limit": voice_channel.user_limit,
                        "bitrate": voice_channel.bitrate,
                        "position": voice_channel.position,
                        "perms": {
                            role.name: {"a": ovw[0].value, "d": ovw[1].value}
                            for role, ovw in voice_channel.overwrites.items()
                        },
                    }
                    if voice_channel.category is not None:
                        voice_channel_data["category"] = voice_channel.category.name
                    backup_data["voice"][str(voice_channel_index)] = voice_channel_data
                    voice_channel_index += 1

                category_index = 0
                for category in ctx.guild.categories:
                    category_data = {
                        "name": category.name.replace(".", ""),
                        "position": category.position,
                        "perms": {
                            role.name: {"a": ovw[0].value, "d": ovw[1].value}
                            for role, ovw in category.overwrites.items()
                        },
                    }
                    backup_data["category"][str(category_index)] = category_data
                    category_index += 1

                role_index = 0
                for role in ctx.guild.roles:
                    if not role.managed and role != ctx.guild.default_role:
                        role_data = {
                            "name": role.name.replace(".", ""),
                            "perms": role.permissions.value,
                            "color": role.colour.value,
                            "hoist": role.hoist,
                            "mentionable": role.mentionable,
                        }
                        backup_data["roles"][str(role_index)] = role_data
                        role_index += 1

                if backups.check_backup(ctx.guild):
                    await backups.add_to_db(
                        {"id": ctx.guild.id, "backup_data": backup_data}
                    )
                else:
                    await backups.add_to_db(
                        {"id": ctx.guild.id, "backup_data": backup_data}
                    )

                embed.colour = 0x43ADF3
                embed.title = "Finished"
                embed.description = "Server backup has been successfully created"
                await msg.edit(embed=embed)

            except (Exception, ExceptionGroup) as e:
                print(e)
                embed.colour = 0x43ADF3
                embed.title = "An error occurred"
                embed.description = "An error occurred when trying to save the server. Roles/channels names can't contain the `$` symbol."
                await ctx.send(embed=embed)

        else:
            embed.colour = 0x43ADF3
            embed.title = "An error occurred"
            embed.description = "This command can only be used by the server owner"
            await ctx.send(embed=embed)

    @backup.command()
    async def load(self, ctx: commands.Context):
        embed = disnake.Embed(color=0x43ADF3)
        embed.title = "Loading Backup"
        embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar)
        msg = await ctx.send(embed=embed)
        if ctx.author == ctx.guild.owner:
            data = backups.get(ctx.guild.id, 0)
            embed.description = "Stage 1 of 6\n> **Restoring the server name**"
            await msg.edit(embed=embed)
            await ctx.guild.edit(name=data["guild"]["name"])
            embed.description = "Stage 2 of 6\n> **Deleting roles**"
            await msg.edit(embed=embed)
            for role in ctx.guild.roles:
                try:
                    await role.delete()
                except (Exception, ExceptionGroup):
                    pass
            embed.description = "Stage 3 of 6\n> **Deleting channels**"
            await msg.edit(embed=embed)
            for channel in ctx.guild.channels:
                try:
                    if channel != ctx.channel:
                        await channel.delete()
                except (Exception, ExceptionGroup):
                    pass
            embed.description = "Stage 4 of 6\n> **Creating roles**"
            await msg.edit(embed=embed)
            for k in range(249, -1, -1):
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
                except (Exception, ExceptionGroup):
                    pass
            embed.description = "Stage 5 of 6\n> **Creating categories**"
            await msg.edit(embed=embed)
            for i in range(500):
                try:
                    overwrites = {}
                    raw_overwrites = data["category"][str(i)]["perms"]
                    for role in ctx.guild.roles:
                        try:
                            ovw = disnake.PermissionOverwrite.from_pair(
                                disnake.Permissions(
                                    permissions=raw_overwrites[role.name]["a"]
                                ),
                                disnake.Permissions(
                                    permissions=raw_overwrites[role.name]["d"]
                                ),
                            )
                            overwrites[role] = ovw
                        except (Exception, ExceptionGroup):
                            pass
                    await ctx.guild.create_category(
                        name=data["category"][str(i)]["name"],
                        position=data["category"][str(i)]["position"],
                        overwrites=overwrites,
                    )
                except (Exception, ExceptionGroup):
                    pass
            embed.description = "Stage 6 of 6\n> **Creating channels**"
            await msg.edit(embed=embed)
            for i in range(500):
                try:
                    overwrites = {}
                    raw_overwrites = data["text"][str(i)]["perms"]
                    for role in ctx.guild.roles:
                        try:
                            ovw = disnake.PermissionOverwrite.from_pair(
                                disnake.Permissions(
                                    permissions=raw_overwrites[role.name]["a"]
                                ),
                                disnake.Permissions(
                                    permissions=raw_overwrites[role.name]["d"]
                                ),
                            )
                            overwrites[role] = ovw
                        except (Exception, ExceptionGroup):
                            pass
                    if data["text"][str(i)]["category"] is None:
                        await ctx.guild.create_text_channel(
                            name=data["text"][str(i)]["name"],
                            topic=data["text"][str(i)]["topic"],
                            nsfw=data["text"][str(i)]["nsfw"],
                            slowmode_delay=data["text"][str(i)]["slowmode"],
                            position=data["text"][str(i)]["position"],
                            overwrites=overwrites,
                        )
                    else:
                        await ctx.guild.create_text_channel(
                            name=data["text"][str(i)]["name"],
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
                except (Exception, ExceptionGroup):
                    pass
            for i in range(500):
                try:
                    overwrites = {}
                    raw_overwrites = data["voice"][str(i)]["perms"]
                    for role in ctx.guild.roles:
                        try:
                            ovw = disnake.PermissionOverwrite.from_pair(
                                disnake.Permissions(
                                    permissions=raw_overwrites[role.name]["a"]
                                ),
                                disnake.Permissions(
                                    permissions=raw_overwrites[role.name]["d"]
                                ),
                            )
                            overwrites[role] = ovw
                        except (Exception, ExceptionGroup):
                            pass
                    if data["voice"][str(i)]["category"] is None:
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
                            category=get(
                                ctx.guild.categories,
                                name=data["voice"][str(i)]["category"],
                            ),
                            overwrites=overwrites,
                        )
                except (Exception, ExceptionGroup):
                    pass
            embed.title = "Finished"
            embed.colour = 0x43ADF3
            embed.description = "Server backup has been successfully loaded"
            await msg.edit(embed=embed)
        else:
            embed.colour = 0x43ADF3
            embed.title = "An error occurred"
            embed.description = "This command can only be used by the server owner"
            await msg.edit(embed=embed)

    @backup.command(aliases=["file"])
    @commands.cooldown(1, 50, commands.BucketType.guild)
    @commands.has_permissions(administrator=True)
    async def _file(self, ctx):
        if backups.check_backup(ctx.guild):
            backup = {
                "guild": {},
                "text_channels": {},
                "voice_channels": {},
                "categories": {},
                "roles": {},
            }
            data = backups.get(ctx.guild.id)
            backup["guild"]["name"] = data["guild"]["name"]
            backup["text_channels"] = data["text"]
            backup["voice_channels"] = data["voice"]
            backup["categories"] = data["category"]
            backup["roles"] = data["roles"]
            with open(str(ctx.guild.id) + ".json", "w") as f:
                json.dump(backup, f, indent=4)
            await ctx.send(file=disnake.File(str(ctx.guild.id) + ".json"))
            os.remove(str(ctx.guild.id) + ".json")
        else:
            embed = disnake.Embed()
            embed.colour = 0x43ADF3
            embed.title = "An error occurred"
            embed.description = "There isn't any backup created for this server"
            await ctx.send(embed=embed)

    @backup.command()
    @commands.has_permissions(administrator=True)
    async def delete(self, ctx):
        embed = disnake.Embed(color=0x43ADF3)
        if backups.check_backup(ctx.guild):
            backups.delete({"_id": ctx.guild.id})
            embed.colour = 0x43ADF3
            embed.title = "Finished"
            embed.description = "Server backup has been successfully deleted"
            await ctx.send(embed=embed)
        else:
            embed = disnake.Embed()
            embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar)
            embed.colour = 0x43ADF3
            embed.title = "An error occurred"
            embed.description = "Server backup hasn't been deleted."
            await ctx.send(embed=embed)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Backup(bot))
