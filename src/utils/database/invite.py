from typing import Any, List, Mapping, Optional, Union, Dict

import disnake

from .base import BaseDatabase


class InviteTrackerDatabase(BaseDatabase):
    def __init__(self, database_name: str) -> None:
        super().__init__(database_name)

    async def get_invites(
        self,
        guild_id: Union[int, str, disnake.Guild],
        to_return: str = None,
    ) -> Optional[Union[List[Mapping[Any, Any]], int, Dict[str, str]]]:
        guild_id = int(guild_id) if isinstance(guild_id, (str, int)) else guild_id.id

        if (
            await self.find_one({"guild_id": guild_id}, return_first_result=True)
            is None
        ):
            return []

        result = await self.find_one({"guild_id": guild_id}, return_first_result=True)
        print(result)
        if result and to_return:
            return result.get(to_return, "")
        return result[0] if result else None

    async def update_invite_info(
        self,
        guild_id: Union[int, str, disnake.Guild],
        inviter: Union[disnake.Member, disnake.User] = None,
        invited: Union[disnake.Member, disnake.User] = None,
    ) -> Optional[Dict[str, str]]:
        if await self.find_one_from_db({"guild_id": guild_id}) is None:
            return await self.add_to_db(
                {
                    "guild_id": guild_id,
                    "invited_id": inviter.id,
                    "count": 0,
                    "invites": [],
                }
            )

        if not inviter and not invited:
            raise Exception(
                "You must provide a inviter (string like message_edit) and/or a logger channel id"
            )

        invites = await self.get_invites(guild_id=guild_id, to_return="invites")

        invites.append(invited)
        count = await self.get_invites(guild_id=guild_id, to_return="count")
        count += 1

        await self.update_db(
            {"guild_id": guild_id},
            {"invites": invites, "count": count},
        )
        return {
            "guild_id": guild_id,
            "inviter_id": inviter.id,
            "invites": invites,
            "count": count,
        }

    async def create_tracker(
        self,
        guild_id: Union[int, str, disnake.Guild],
        inviter_id: Union[disnake.Member, disnake.User],
        invited_user: Union[disnake.Member, disnake.User],
    ) -> None:
        guild_id = (
            guild_id.id
            if isinstance(guild_id, disnake.Guild)
            else int(guild_id)
            if isinstance(guild_id, str)
            else guild_id
        )
        count = await self.get_invites(guild_id=guild_id, to_return="count")
        invites = await self.get_invites(guild_id=guild_id, to_return="invites")
        invites.append(invited_user)

        return await self.update_db(
            {"guild_id": guild_id},
            {"invited_id": inviter_id.id, "count": count + 1, "invites": invites},
        )
