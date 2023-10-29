import disnake

from .base import BaseDatabase
from typing import Dict, Any, Union


class BackupsDatabase(BaseDatabase):
    def __init__(self, database_name: str) -> None:
        super().__init__(database_name)

    def check_backup(self, guild):
        return self.collection_cache.get(guild.id, 0) != 0

    async def update_ticket_info(
        self,
        guild_id: Union[int, str, disnake.Guild],
        ticket_name: str,
        ticket_description: str,
        ticket_channel_id: int,
    ) -> int:
        if await self.find_one_from_db({"guild_id": guild_id}) is None:
            await self.add_to_db(
                {
                    "guild_id": guild_id,
                    "tickets": [
                        {
                            "ticket_name": ticket_name,
                            "ticket_description": ticket_description,
                            "ticket_channel_id": ticket_channel_id,
                        }
                    ],
                }
            )

        tickets = await self.get_tickets(guild_id=guild_id)
        tickets.append(
            {
                "ticket_name": ticket_name,
                "ticket_description": ticket_description,
                "ticket_channel_id": ticket_channel_id,
            }
        )
        await self.update_db(
            {"guild_id": guild_id},
            {"tickets": tickets},
        )
