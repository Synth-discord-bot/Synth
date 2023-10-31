from .base import BaseDatabase

from typing import Any, List, Mapping, Union, Dict
import disnake


class BackupsDatabase(BaseDatabase):
    def __init__(self, database_name: str) -> None:
        super().__init__(database_name)

    def check_backup(self, guild) -> bool:
        return len(self.get_items_in_cache({"guild_id": guild.id})) != 0

    async def get(
        self,
        guild_id: Union[int, str, disnake.Guild],
        to_return: str = None,
    ) -> Union[Union[Dict[str, Any], Mapping[str, Any]], List[Any]]:
        guild_id = str(guild_id) if isinstance(guild_id, (str, int)) else guild_id.id

        if await self.find_one_from_db({"guild_id": guild_id}) is None:
            return []
        result = await self.find_one_from_db({"guild_id": guild_id})
        if result and to_return:
            return result.get(to_return, None)
        if result:
            return result

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
        backups = await self.get(guild_id=guild_id, to_return="backup_data")
        backups.update(
            {
                "backup_data": backup_data,
            }
        )
        await self.update_db(
            {"guild_id": guild_id},
            {"backup_data": backup_data},
        )
