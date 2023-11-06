from datetime import datetime
from typing import Union, Dict, Any

import disnake

from .base import BaseDatabase


class WarnDatabase(BaseDatabase):
    def __init__(self, database_name: str) -> None:
        super().__init__(database_name=database_name)

    async def add_warn(self, guild_id: int, administrator: disnake.Member, user: disnake.Member, reason: str) -> int:
        """
        Add a warning for a user in the database.
        :param administrator: Administrator who gave the warn
        :param guild_id: The ID of the guild where the warning is issued.
        :param user: The disnake.Member object representing the user being warned.
        :param reason: The reason for the warning.
        :return: The case number of the warning.
        """

        # Fetch the existing warnings for the guild
        warns_data = await self.find_one_from_db({"guild_id": guild_id})
        if not warns_data:
            warns_data = {
                "guild_id": guild_id,
                "warnings": {}  # A dictionary to store user warnings
            }

        # Check if the user already has warnings, or initialize an empty list
        user_warnings = warns_data["warnings"].get(str(user.id), [])

        # Get the current Unix timestamp (seconds since epoch)
        timestamp = int(datetime.now().timestamp())

        # Add the new warning to the user's list of warnings with a timestamp
        new_case = {
            "moderator_id": administrator.id,
            "reason": reason,
            "timestamp": timestamp
        }
        user_warnings.append(new_case)

        # Update the warnings for the user in the guild's data
        warns_data["warnings"][str(user.id)] = user_warnings

        # Update the database with the modified guild data
        await self.update_db({"guild_id": guild_id}, warns_data)

        # Return the case number of the new warning (index of the new warning in the user's list)
        return len(user_warnings)

    async def get_user_warnings(self, guild_id: int, user: disnake.Member) -> list:
        """
        Get the list of warnings for a specific user in a guild.
        :param guild_id: The ID of the guild where the user's warnings are stored.
        :param user: The disnake.Member object representing the user.
        :return: A list of warning cases for the user (including reason and timestamp).
        """
        # Fetch the existing warnings for the guild
        warns_data = await self.find_one_from_db({"guild_id": guild_id})
        if not warns_data:
            return []  # No warnings data for the guild

        # Check if the user has warnings, or return an empty list
        user_warnings = warns_data["warnings"].get(str(user.id), [])
        return user_warnings

    async def delete_warnings(self, guild_id: int, user: Union[int, disnake.Member], amount: int) -> int | None:
        user_id = user.id if isinstance(user, disnake.Member) else user

        # Fetch the existing warnings for the guild
        warns_data = await self.find_one({"guild_id": guild_id}, return_first_result=True)
        if not warns_data:
            return None  # No warnings data for the guild

        # Check if the user has warnings, or return 0
        user_warnings = warns_data["warnings"].get(str(user_id), None)
        if not user_warnings:
            return 0

        # Ensure we don't remove more warnings than available
        if amount > len(user_warnings):
            amount = len(user_warnings)

        # Remove the specified number of warnings
        removed_warnings = user_warnings[:amount]
        user_warnings = user_warnings[amount:]

        # Update the warnings for the user in the guild's data
        warns_data["warnings"][str(user_id)] = user_warnings

        # Update the database with the modified guild data
        await self.update_db({"guild_id": guild_id}, {"warnings": warns_data["warnings"]})

        return len(removed_warnings)
