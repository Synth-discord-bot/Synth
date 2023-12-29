from typing import Optional, List

import disnake

from .base import BaseDatabase


class MainDatabase(BaseDatabase):
    def __init__(self, database_name: str) -> None:
        super().__init__(database_name)

    def get_cooldown(self, guild_id: int) -> Optional[int]:
        if custom_cd := self.get_items_in_cache(
            {"id": guild_id}, to_return="custom_cd"
        ):
            return custom_cd  # type: ignore

    # prefixes

    def get_prefix_from_cache(self, guild_id: int) -> Optional[str]:
        if prefix := self.get_items_in_cache({"id": guild_id}, to_return="prefix"):
            return prefix  # type: ignore

        return ">>"

    async def get_prefix(self, guild_id: int) -> Optional[str]:
        if await self.find_one_from_db({"id": guild_id}) is None:
            return ">>"

        return (await self.find_one_from_db({"id": guild_id})).get("prefix", ">>")

    async def set_prefix(self, guild_id: int, prefix: str) -> None:
        if await self.find_one_from_db({"id": guild_id}) is None:
            return await self.add_to_db({"id": guild_id, "prefix": prefix})

        return await self.update_db({"id": guild_id}, {"prefix": prefix})

    async def _get_commands_list(self, guild_id: int) -> List[str]:
        if await self.find_one_from_db({"id": guild_id}) is None:
            return []

        return (await self.find_one_from_db({"id": guild_id})).get(
            "disabled_commands", []
        )

    async def add_embed_color(self, guild_id: int, embed_color: hex) -> Optional[int]:
        if await self.find_one_from_db({"id": guild_id}) is None:
            return await self.add_to_db({"id": guild_id, "embed_color": embed_color})

        return await self.update_db({"id": guild_id}, {"embed_color": embed_color})

    async def get_embed_color(self, guild_id: int) -> Optional[int]:
        if await self.find_one_from_db({"id": guild_id}) is None:
            return None
        return (await self.find_one_from_db({"id": guild_id})).get(
            "embed_color", 0x2F3236
        )

    async def check_command(
        self, guild_id: int, command: str, add_if_not_exists: bool = True
    ) -> bool:
        if await self.find_one_from_db({"id": guild_id}) is None and add_if_not_exists:
            await self.update_db({"id": guild_id}, {"disabled_commands": [command]})

        commands_list = await self._get_commands_list(guild_id=guild_id)
        return command in commands_list

    async def add_command(self, guild_id: int, command: str) -> None:
        if await self.find_one_from_db({"id": guild_id}) is None:
            return await self.update_db(
                {"id": guild_id}, {"disabled_commands": [command]}
            )

        if not await self.check_command(guild_id=guild_id, command=command):
            commands = await self._get_commands_list(guild_id=guild_id)
            commands.append(command)
            await self.update_db({"id": guild_id}, {"disabled_commands": commands})

    async def delete_command(self, guild_id: int, command: str) -> None:
        if await self.find_one_from_db({"id": guild_id}) is None:
            return await self.update_db({"id": guild_id}, {"disabled_commands": []})

        commands = await self._get_commands_list(guild_id=guild_id)
        commands.remove(command)

        await self.update_db({"id": guild_id}, {"disabled_commands": commands})
