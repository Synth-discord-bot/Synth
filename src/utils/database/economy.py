from typing import Union

import disnake

from .base import BaseDatabase


class Economy(BaseDatabase):
    def __init__(self, database_name: str) -> None:
        super().__init__(database_name)

    async def get_balance(
        self, user_id: Union[int, str, disnake.User, disnake.Member]
    ) -> int:
        user_id = int(user_id) if isinstance(user_id, (str, int)) else user_id.id

        return (await self.find_one_from_db({"id": user_id})).get("balance", 0)

    async def get_bank(
        self, user_id: Union[int, str, disnake.User, disnake.Member]
    ) -> int:
        user_id = int(user_id) if isinstance(user_id, (str, int)) else user_id.id

        return (await self.find_one_from_db({"id": user_id})).get("bank", 0)
