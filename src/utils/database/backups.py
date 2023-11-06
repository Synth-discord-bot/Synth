from typing import Any, List, Mapping, Union, Dict

import disnake

from .base import BaseDatabase


class BackupDatabase(BaseDatabase):
    def __init__(self, database_name: str) -> None:
        super().__init__(database_name)

    def check_backup(self, guild):
        return len(self.get_items_in_cache({"guild_id": guild.id})) != 0

    async def get(
        self,
        guild_id: Union[int, str, disnake.Guild],
        to_return: str = None,
    ) -> Union[Union[Dict[str, Any], Mapping[str, Any]], List[Any]]:
        guild_id = int(guild_id) if isinstance(guild_id, (str, int)) else guild_id.id

        if await self.find_one_from_db({"guild_id": guild_id}) is None:
            return []
        result = await self.find_one_from_db({"guild_id": guild_id})
        if result and to_return:
            return result.get(to_return, None)
        if result:
            return result
        else:
            return []

    async def update_backups_info(
        self,
        guild_id: Union[int, str, disnake.Guild],
        backup_data: Union[dict],
    ) -> None:
        if await self.find_one_from_db({"guild_id": guild_id}) is None:
            return await self.add_to_db(
                {
                    "guild_id": guild_id,
                    "backup_data": backup_data,
                }
            )
        backups = await self.get(guild_id=guild_id)
        backups.update(
            {
                "backup_data": backup_data,
            }
        )
        await self.update_db(
            {"guild_id": guild_id},
            {"backup_data": backup_data},
        )
        self._add_to_cache({"guild_id": guild_id, "backup_data": backup_data})

    async def delete_backup(self, guild_id: int) -> Mapping[str, Any]:
        """Delete backup from a database

        returns: Dictionary of a last backup (if exists)
        """
        if await self.find_one_from_db({"guild_id": guild_id}) is not None:
            result = await self.find_one_from_db({"guild_id": guild_id})
            await self.remove_from_db({"guild_id": guild_id})
            if result:
                return result
