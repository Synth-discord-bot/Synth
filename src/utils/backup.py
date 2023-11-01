from datetime import datetime
from typing import Dict, Any, Union

import disnake


class Backup:
    def __init__(
        self,
        guild: disnake.Guild,
    ) -> None:
        self.guild: disnake.Guild = guild

    async def create(self) -> Dict[Any, Any]:
        """Creates a backup of a guild"""
        return await BackupCreator(self.guild).create_backup()


class BackupCreator:
    def __init__(self, guild: disnake.Guild) -> None:
        self.guild: disnake.Guild = guild

    async def create_backup(
        self,
    ) -> Dict[str, Union[Dict[Any, Any], Dict[str, str], Dict[str, int]]]:
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
                "description": self.guild.description,
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
