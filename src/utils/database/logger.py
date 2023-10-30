from typing import Any, List, Mapping, Union

import disnake

from .base import BaseDatabase


class LoggerDatabase(BaseDatabase):
    def __init__(self, database_name: str) -> None:
        super().__init__(database_name)

    async def get_loggers(
        self,
        guild_id: Union[int, str, disnake.Guild],
        return_first_logger: bool = False,
    ) -> List[Mapping[Any, Any]]:
        guild_id = int(guild_id) if isinstance(guild_id, (str, int)) else guild_id.id

        if await self.find_one_from_db({"guild_id": guild_id}) is None:
            return []
        result = (await self.find_one_from_db({"guild_id": guild_id})).get(
            "loggers", []
        )
        if return_first_logger and result:
            return result[0]
        return result

    async def update_logger_info(
        self,
        guild_id: Union[int, str, disnake.Guild],
        logger_channel_id: int,
    ) -> int:
        if await self.find_one_from_db({"guild_id": guild_id}) is None:
            await self.add_to_db(
                {
                    "guild_id": guild_id,
                    "loggers": [],
                }
            )

        loggers = await self.get_loggers(guild_id=guild_id)
        loggers.append(
            {
                "logger_channel_id": logger_channel_id,
            }
        )
        await self.update_db(
            {"guild_id": guild_id},
            {"loggers": loggers},
        )
