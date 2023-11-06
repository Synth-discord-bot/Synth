from typing import Any, Mapping, Union, List, Optional, Dict

import disnake
from disnake import Member

from .base import BaseDatabase


class PrivateRoomsDatabase(BaseDatabase):
    def __init__(self, database_name: str) -> None:
        super().__init__(database_name=database_name)

    async def get_private_room(
        self, guild_id: int, to_return: str = None
    ) -> Union[List[Dict[str, Any]], Mapping[str, Any], None]:
        if result := await self.find_one_from_db({"guild_id": guild_id}):
            if result and to_return:
                return result.get(to_return, None)
            return result
        else:
            return None

    async def create_main_room(
        self, guild_id: int, voice_channel: disnake.VoiceChannel
    ) -> None:
        await self.add_to_db(
            {"guild_id": guild_id, "main_channel_id": voice_channel.id, "channels": []}
        )

    async def create_private_room(
        self, member: Member, voice_channel: disnake.VoiceChannel
    ) -> None:
        result = await self.get_private_room(member.guild.id)
        if not result:
            return None

        channels = await self.get_private_room(member.guild.id, to_return="channels")
        channels.append({"channel_id": voice_channel.id, "owner_id": member.id})

        await self.update_db({"guild_id": member.guild.id}, {"channels": channels})

    async def delete_private_room(
        self, member: Member, voice_channel: disnake.VoiceChannel
    ):
        if result := await self.get_private_room(member.guild.id, to_return="channels"):
            for result_dict in result:
                if voice_channel.id in result_dict.values():
                    del result_dict
                    break

            await self.update_db({"guild_id": member.guild.id}, {"channels": result})

    async def get_owner_id(
        self, guild_id: int, voice_channel: disnake.VoiceChannel
    ) -> Optional[int]:
        if result := await self.get_private_room(
            guild_id=guild_id, to_return="channels"
        ):
            for room in result:
                if room.get("channel_id") == voice_channel.id:
                    return room.get("owner_id", None) or None
        return None

    async def set_owner(
        self, guild_id: int, voice_channel: disnake.VoiceChannel, member: Member
    ) -> None:
        if channels := await self.get_private_room(
            guild_id=guild_id, to_return="channels"
        ):
            for index, channel in enumerate(channels):
                if channel.get("channel_id") == voice_channel.id:
                    channels[index]["owner_id"] = member.id
                    break

            await self.update_db({"guild_id": guild_id}, {"channels": channels})
