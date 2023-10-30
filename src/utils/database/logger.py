from typing import Any, List, Mapping, Union, Dict

import disnake

from .base import BaseDatabase


class LoggerDatabase(BaseDatabase):
    def __init__(self, database_name: str) -> None:
        super().__init__(database_name)

    async def get_loggers(
        self,
        guild_id: Union[int, str, disnake.Guild],
        to_return: str = None,
    ) -> Union[List[Mapping[Any, Any]], int, Dict[str, str]]:
        guild_id = int(guild_id) if isinstance(guild_id, (str, int)) else guild_id.id

        if (
            await self.find_one({"guild_id": guild_id}, return_first_result=True)
            is None
        ):
            return []

        result = (
            await self.find_one({"guild_id": guild_id}, return_first_result=True)
        ).get("loggers", [])
        if to_return and result:
            return result[0].get(to_return, "")
        return result[0]

    async def update_logger_info(
        self,
        guild_id: Union[int, str, disnake.Guild],
        logger_type: str = None,
        logger_channel_id: str = None,
    ) -> Dict[str, str]:
        if await self.find_one_from_db({"guild_id": guild_id}) is None:
            await self.add_to_db(
                {
                    "guild_id": guild_id,
                    "loggers": [],
                }
            )

        if not logger_type and not logger_channel_id:
            raise Exception(
                "You must provide a logger type (string like message_edit) and/or a logger channel id"
            )

        loggers = await self.get_loggers(guild_id=guild_id)

        # check if "key" exists in DB
        if logger_type not in loggers:
            loggers.append({logger_type: logger_channel_id})
        else:
            loggers.update({logger_type: logger_channel_id})

        await self.update_db(
            {"guild_id": guild_id},
            {"loggers": loggers},
        )
        return {logger_type: logger_channel_id}

    async def create_logger(
        self,
        guild_id: Union[int, str, disnake.Guild],
        main_log_channel: disnake.TextChannel,
        guild_log_channel: disnake.TextChannel = None,
        invite_log_channel: disnake.TextChannel = None,
        message_log_channel: disnake.TextChannel = None,
    ) -> None:
        guild_id = (
            guild_id.id
            if isinstance(guild_id, disnake.Guild)
            else int(guild_id)
            if isinstance(guild_id, str)
            else guild_id
        )
        return await self.update_db(
            {"guild_id": guild_id},
            {
                "loggers": [
                    {
                        "main": main_log_channel.id,
                        "message": message_log_channel.id,
                        "invite": invite_log_channel.id,
                        "guild": guild_log_channel.id,
                    },
                ]
            },
        )
