from typing import Any, List, Mapping, Union

import disnake

from .base import BaseDatabase


class FormsDatabase(BaseDatabase):
    def __init__(self, database_name: str) -> None:
        super().__init__(database_name)

    async def get_forms(
        self,
        guild_id: Union[int, str, disnake.Guild],
        return_first_form: bool = False,
    ) -> List[Mapping[Any, Any]]:
        guild_id = int(guild_id) if isinstance(guild_id, (str, int)) else guild_id.id

        if await self.find_one_from_db({"guild_id": guild_id}) is None:
            return []
        result = (await self.find_one_from_db({"guild_id": guild_id})).get("forms", [])
        if return_first_form and result:
            return result[0]
        return result

    async def update_form_info(
        self,
        guild_id: Union[int, str, disnake.Guild],
        form_name: str,
        form_description: str,
        form_channel_id: int,
        form_type: str,
    ) -> int:
        if await self.find_one_from_db({"guild_id": guild_id}) is None:
            await self.add_to_db(
                {
                    "guild_id": guild_id,
                    "forms": [],
                }
            )

        form = await self.get_forms(guild_id=guild_id)
        form.append(
            {
                "form_name": form_name,
                "form_description": form_description,
                "form_channel_id": form_channel_id,
                "form_type": form_type,
            }
        )
        await self.update_db(
            {"guild_id": guild_id},
            {"forms": form},
        )
