from typing import Any, Dict

from .base import BaseDatabase


class GiveawayDatabase(BaseDatabase):
    def __init__(self, database_name: str) -> None:
        super().__init__(database_name=database_name)

    async def insert_giveaway(
        self,
        channel_id: int,
        message_id: int,
        end_time: Any,
        winners: int,
        embed: Dict[Any, Any],
        prize: str,
    ) -> None:
        await self.add_to_db(
            {
                # "guild_id": None,
                "channel_id": channel_id,
                "message_id": message_id,
                "end_time": end_time,
                "winner_amount": winners,
                "embed_data": embed,
                "prize": prize,
            }
        )

    async def delete_giveaway(self, value: Dict[Any, Any]):
        await self.remove_from_db(value)
