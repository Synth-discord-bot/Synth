import logging
from typing import Any, Mapping, Optional, Union, List
import disnake

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCursor

_client = AsyncIOMotorClient("mongodb://127.0.0.1:27017")
database = _client["synth"]


class BaseDatabase:
    def __init__(self, database_name: str) -> None:
        self.collection = database[database_name]
        self.collection_cache = {}

    def _add_to_cache(self, param_filter: Mapping[str, Any]) -> Any:
        """
        :param param_filter: dictionary to add
        :return: added item

        Example code to search in cache:

        # Here's the dictionary that will be added in the database: {"id": 1, "test": True}

        add_to_cache(1, {"id": 1, "test": True}) # 1 is the uid argument, {"id": 1, "test": True} is the param_filter
        """
        index = len(self.collection_cache) + 1
        self.collection_cache[index] = param_filter
        return param_filter

    async def get_items_in_db(
            self,
            find_dict: Mapping[str, Any],
            to_list: bool = True,
            count: Union[int, None] = None,
    ) -> Union[List[Mapping[str, Any]], AsyncIOMotorCursor]:
        result = self.collection.find(filter=find_dict)
        if to_list:
            return await result.to_list(length=count)

        return result

    def get_items_in_cache(self, query: Any) -> List[Any]:
        """
        Get items from cache by Mongo DB algorithm

        Args:
            query (Any): Query to search

        Returns:
            List[Any]: List of available items
        """
        return [
            {key: value}
            for key, value in self.collection_cache.items()
            if all(k in value and value[k] == v for k, v in query.items())
        ]

    async def find_one_from_cache(self, value: Any) -> Any:
        results = self.get_items_in_cache(value)
        return results[0] if results else None

    async def find_one_from_db(
            self, param_filter: Mapping[str, Any]
    ) -> Mapping[str, Any]:
        results = await self.get_items_in_db(find_dict=param_filter, to_list=True)
        return results[0] if len(results) >= 1 else None

    async def find_one(self, value: Union[Mapping[str, Any], Any]) -> Any:
        # try to search in cache
        results = self.get_items_in_cache(value)
        if results:
            return results[0]

        # if not found in cache, search in database
        results = await self.get_items_in_db(value)
        if results:
            return results[0]

        return None  # None if not found

    async def add_to_db(self, data: Mapping[str, Any]) -> None:
        await self.collection.insert_one(data)
        self._add_to_cache(data)

    async def fetch_and_cache_all(self) -> None:
        results = await self.get_items_in_db({}, to_list=True)
        logging.info(f"Found {len(results)} items in database")
        for index, data in enumerate(results, start=1):
            self.collection_cache[index] = data

    async def update_db(
            self, data: Mapping[str, Any], new_value: Mapping[str, Any]
    ) -> None:
        await self.collection.update_one(data, {"$set": new_value}, upsert=True)


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


class MainDatabase(BaseDatabase):
    def __init__(self, database_name: str) -> None:
        super().__init__(database_name)

    # prefixes
    async def get_prefix(self, guild_id: int) -> Optional[str]:
        if await self.find_one_from_db({"id": guild_id}) is None:
            return ">>"

        return (await self.find_one_from_db({"id": guild_id})).get("prefix", ">>")

    async def set_prefix(self, guild_id: int, prefix: str) -> None:
        if await self.find_one_from_db({"id": guild_id}) is None:
            return await self.add_to_db({"id": guild_id, "prefix": prefix})

        return await self.update_db({"id": guild_id}, {"prefix": prefix})

    async def _get_commands_list(self, guild_id: int) -> List[str]:
        if await self.find_one_from_db({"id": guild_id}) is None:
            return []

        return (await self.find_one_from_db({"id": guild_id})).get("disabled_commands", [])

    async def check_command(self, guild_id: int, command: str) -> bool:
        if await self.find_one_from_db({"id": guild_id}) is None:
            await self.update_db({"id": guild_id}, {"disabled_commands": [command]})

        commands_list = await self._get_commands_list(guild_id=guild_id)
        return command in commands_list

    async def add_command(self, guild_id: int, command: str) -> None:
        if await self.find_one_from_db({"id": guild_id}) is None:
            return await self.update_db({"id": guild_id}, {"disabled_commands": [command]})

        if not await self.check_command(guild_id=guild_id, command=command):
            commands = await self._get_commands_list(guild_id=guild_id)
            commands.append(command)
            await self.update_db({"id": guild_id}, {"disabled_commands": commands})
