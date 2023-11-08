import asyncio
import base64
from datetime import datetime
from io import BytesIO
from typing import Dict, Any, Union

import aiohttp
import disnake
from disnake.utils import get


class Backup:
    def __init__(
            self,
            guild: disnake.Guild,
    ) -> None:
        self.guild: disnake.Guild = guild

    async def create(self) -> Dict[Any, Any]:
        """Creates a backup of a guild"""
        return await BackupCreator(self.guild).create_backup()

    async def restore(
            self,
            data: Dict[Any, Any],
            message: Union[disnake.Message, disnake.MessageInteraction],
    ) -> None:
        """Restores a backup of a guild"""
        embed = disnake.Embed(color=0x2F3136)
        embed.title = "<a:loading:1168599537682755584> Loading Backup"
        embed.set_footer(text=message.author, icon_url=message.author.avatar)

        embed.description = (
            "<:info:1169685342077583480> Stage 1 of 6\n> **Deleting channels**"
        )
        await message.edit_original_response(embed=embed, view=None)

        for channel in self.guild.channels:
            try:
                if channel != message.channel:
                    await channel.delete()
            except (disnake.Forbidden, disnake.NotFound, disnake.HTTPException):
                continue

        embed.description = (
            "<:info:1169685342077583480> Stage 2 of 6\n> **Deleting roles**"
        )
        await message.edit_original_response(embed=embed, view=None)

        for role in self.guild.roles:
            try:
                await role.delete()
            except (disnake.Forbidden, disnake.HTTPException):
                continue

        embed.description = (
            "<:info:1169685342077583480> Stage 3 of 6\n> **Creating roles**"
        )
        await message.edit_original_response(embed=embed, view=None)

        roles = data["roles"]
        for k in range(len(roles) + 1):
            try:
                if roles.get(str(k), None):
                    await self.guild.create_role(
                        name=roles[str(k)]["name"],
                        colour=disnake.Colour(value=roles[str(k)]["color"]),
                        permissions=disnake.Permissions(
                            permissions=roles[str(k)]["perms"]
                        ),
                        hoist=roles[str(k)]["hoist"],
                        mentionable=roles[str(k)]["mentionable"],
                    )
            except (
                    disnake.NotFound,
                    disnake.Forbidden,
                    disnake.HTTPException,
                    TypeError,
            ):
                continue

        embed.description = (
            "<:info:1169685342077583480> Stage 4 of 6\n> **Creating categories**"
        )
        await message.edit_original_response(embed=embed, view=None)

        categories = data["category"]
        for i in range(len(categories) + 1):
            try:
                overwrites = {}
                if data["category"].get(str(i), None) is not None:
                    raw_overwrites = data["category"][str(i)]["perms"]

                    for role_to_recovery in self.guild.roles:
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

                    await self.guild.create_category(
                        name=categories[str(i)]["name"],
                        position=categories[str(i)]["position"],
                        overwrites=overwrites,
                    )
            except (disnake.Forbidden, disnake.HTTPException, TypeError):
                continue

        embed.description = (
            "<:info:1169685342077583480> Stage 5 of 6\n> **Creating channels**"
        )
        await message.edit_original_response(embed=embed, view=None)

        text_channels = data["text"]
        for i in range(len(text_channels) + 1):
            try:
                overwrites = {}
                if text_channels.get(str(i), None) is not None:
                    raw_overwrites = text_channels[str(i)]["perms"]

                    for old_role_permissions in self.guild.roles:
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
                    current_channel_name = message.channel.name

                    if new_channel_name != current_channel_name:
                        if text_channels[str(i)].get("category", None) is None:
                            await self.guild.create_text_channel(
                                name=new_channel_name,
                                topic=text_channels[str(i)]["topic"],
                                nsfw=text_channels[str(i)]["nsfw"],
                                slowmode_delay=text_channels[str(i)]["slowmode"],
                                position=text_channels[str(i)]["position"],
                                overwrites=overwrites,
                            )
                        else:
                            await self.guild.create_text_channel(
                                name=new_channel_name,
                                topic=data["text"][str(i)]["topic"],
                                nsfw=data["text"][str(i)]["nsfw"],
                                slowmode_delay=data["text"][str(i)]["slowmode"],
                                position=data["text"][str(i)]["position"],
                                category=get(
                                    self.guild.categories,
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
                if voice_channels.get(str(i), None) is not None:
                    raw_overwrites = voice_channels[str(i)]["perms"]

                    for old_role_permissions in self.guild.roles:
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

                    if voice_channels[str(i)].get("category", None) is None:
                        await self.guild.create_voice_channel(
                            name=voice_channels[str(i)]["name"],
                            user_limit=voice_channels[str(i)]["limit"],
                            bitrate=voice_channels[str(i)]["bitrate"],
                            position=voice_channels[str(i)]["position"],
                            overwrites=overwrites,
                        )
                    else:
                        await self.guild.create_voice_channel(
                            name=voice_channels[str(i)]["name"],
                            user_limit=voice_channels[str(i)]["limit"],
                            bitrate=voice_channels[str(i)]["bitrate"],
                            position=voice_channels[str(i)]["position"],
                            category=get(  # TODO: FIX
                                self.guild.categories,
                                name=voice_channels[str(i)]["category"],
                            ),
                            overwrites=overwrites,
                        )
            except (disnake.Forbidden, disnake.HTTPException, TypeError):
                continue

        embed.description = "<:info:1169685342077583480> Stage 6 of 6\n> **Restoring the server main information**"
        await message.edit_original_response(embed=embed, view=None)

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

        ver_level_mongo = data.get("guild")["verification_level"][0]
        ver_level = verification_level_mapping.get(
            ver_level_mongo, disnake.VerificationLevel.none
        )

        afk_channel = disnake.utils.get(
            self.guild.voice_channels, name=data["guild"]["afk_channel"]
        )
        system_channel = disnake.utils.get(
            self.guild.text_channels, name=data["guild"]["system_channel"]
        )
        rules_channel = disnake.utils.get(
            self.guild.text_channels, name=data["guild"]["rules_channel"]
        )

        await self.guild.edit(
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

        await message.edit_original_response(embed=embed, view=None)


class BackupCreator:
    def __init__(self, guild: disnake.Guild) -> None:
        self.guild: disnake.Guild = guild

    async def create_backup(
            self,
    ) -> Dict[str, Union[Dict[Any, Any], Dict[str, str], Dict[str, int]]]:
        icon_data = None  # Default to None
        banner_data = None  # Default to None

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.guild.icon.url) as icon_response:
                    if icon_response.status == 200:
                        icon_data = base64.b64encode(await icon_response.read()).decode(
                            "utf-8"
                        )
        except (Exception, disnake.Forbidden):
            pass
        finally:
            await session.close()

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.guild.banner.url) as banner_response:
                    if banner_response.status == 200:
                        banner_data = base64.b64encode(
                            await banner_response.read()
                        ).decode("utf-8")
        except (Exception, disnake.Forbidden):
            pass
        finally:
            await session.close()

        backup_data = {
            "info": {
                "nextsave": 2147483647,
                "interval": 0,
                "created": int(datetime.now().timestamp()),
            },
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
                "premium_progress_bar_enabled": self.guild.premium_progress_bar_enabled,
                "verification_level": self.guild.verification_level
                if self.guild.verification_level
                else disnake.VerificationLevel.none,
                "system_channel": self.guild.system_channel.name
                if self.guild.system_channel
                else None,
                "description": self.guild.description,
                "icon": icon_data if self.guild.icon else None,
                "banner": banner_data if self.guild.banner else None,
            },
            "text": {},
            "voice": {},
            "category": {},
            "roles": {},
        }

        for index, text_channel in enumerate(self.guild.text_channels):
            text_dict = {
                "name": text_channel.name,
                "topic": (
                    text_channel.topic.replace(".", "") if text_channel.topic else None
                ),
                "slowmode": text_channel.slowmode_delay,
                "nsfw": text_channel.nsfw,
                "position": text_channel.position,
                "perms": {
                    role.name: {
                        "a": ovw.pair()[0].value,
                        "d": ovw.pair()[1].value,
                    }
                    for role, ovw in text_channel.overwrites.items()
                },
            }

            if text_channel.category:
                text_dict["category"] = text_channel.category.name

            backup_data["text"].setdefault(str(index), {}).update(text_dict)

        for index, voice_channel in enumerate(self.guild.voice_channels):
            voice_dict = {
                "name": voice_channel.name.replace(".", " "),
                "limit": voice_channel.user_limit,
                "bitrate": voice_channel.bitrate,
                "position": voice_channel.position,
                "perms": {
                    role.name: {
                        "a": ovw.pair()[0].value,
                        "d": ovw.pair()[1].value,
                    }
                    for role, ovw in voice_channel.overwrites.items()
                },
            }
            if voice_channel.category:
                voice_dict["category"] = voice_channel.category.name

            backup_data["voice"].setdefault(str(index), {}).update(voice_dict)

        for index, category in enumerate(self.guild.categories):
            category_dict = {
                "name": category.name.replace(".", ""),
                "position": category.position,
                "perms": {
                    role.name: {
                        "a": ovw.pair()[0].value,
                        "d": ovw.pair()[1].value,
                    }
                    for role, ovw in category.overwrites.items()
                },
            }
            backup_data["category"].setdefault(str(index), {}).update(category_dict)

        for index, role in enumerate(self.guild.roles):
            if not role.managed and role != self.guild.default_role:
                role_data = {
                    "name": role.name.replace(".", ""),
                    "perms": role.permissions.value,
                    "color": role.colour.value,
                    "hoist": role.hoist,
                    "mentionable": role.mentionable,
                }
                backup_data["roles"].setdefault(str(index), {}).update(role_data)

        return backup_data
