from .base import BaseDatabase

from typing import Any, List, Mapping, Union, Dict
import disnake


class BackupsDatabase(BaseDatabase):
    def __init__(self, database_name: str) -> None:
        super().__init__(database_name)

    def check_backup(self, guild):
        return len(self.collection_cache[1]) != 0

    async def get(
        self,
        guild_id: Union[int, str, disnake.Guild],
    ) -> Union[Union[Dict[str, Any], Mapping[str, Any]], List[Any]]:
        guild_id = int(guild_id) if isinstance(guild_id, (str, int)) else guild_id.id

        if await self.find_one_from_db({"guild_id": guild_id}) is None:
            return []
        result = await self.find_one_from_db({"guild_id": guild_id})
        if result:
            return result

    async def update_backups_info(
        self,
        guild_id: Union[int, str, disnake.Guild],
        backup_data: Union[dict],
    ) -> None:
        if await self.find_one_from_db({"guild_id": guild_id}) is None:
            await self.add_to_db(
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
