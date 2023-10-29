from typing import Any, List, Mapping, Union

import disnake

from .base import BaseDatabase


class TicketDatabase(BaseDatabase):
    def __init__(self, database_name: str) -> None:
        super().__init__(database_name)

    async def get_tickets(
        self,
        guild_id: Union[int, str, disnake.Guild],
        return_first_ticket: bool = False,
    ) -> List[Mapping[Any, Any]]:
        guild_id = int(guild_id) if isinstance(guild_id, (str, int)) else guild_id.id

        if await self.find_one_from_db({"guild_id": guild_id}) is None:
            return []
        result = (await self.find_one_from_db({"guild_id": guild_id})).get(
            "tickets", []
        )
        if return_first_ticket and result:
            return result[0]
        return result

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
