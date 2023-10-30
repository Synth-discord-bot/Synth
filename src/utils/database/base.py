import logging
from typing import Any, Dict, Mapping, Union, List

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCursor


class BaseDatabase:
    def __init__(self, database_name: str) -> None:
        self._client = AsyncIOMotorClient("mongodb://127.0.0.1:27017")
        self._database = self._client["synth"]
        self.collection = self._database[database_name]
        self.collection_cache: List[Dict[str, Any]] = []
        self.name = database_name

    def _add_to_cache(self, param_filter: Mapping[str, Any]) -> Any:
        """
        :param param_filter: dictionary to add
        :return: added item

        Example code to search in cache:

        # Here's the dictionary that will be added in the database: {"id": 1, "test": True}

        add_to_cache({"id": 1, "test": True}) # 1 is the uid argument, {"id": 1, "test": True} is the param_filter
        """
        # index = len(self.collection_cache) + 1
        self.collection_cache.append(param_filter)
        return param_filter

    def _update_cache(
        self, old_value: Mapping[str, Any], new_value: Mapping[str, Any]
    ) -> Any:
        try:
            index = self.collection_cache.index(old_value)
            self.collection_cache[index].update(new_value)
        except ValueError:
            self.collection_cache.append(new_value)

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
        # return [
        #     {key: value}
        #     for key, value in self.collection_cache.items()
        #     if all(k in value and value[k] == v for k, v in query.items())
        # ]
        return [
            {key: value}
            for item in self.collection_cache
            for key, value in item.items()
            if all(k == value and value[k] == v for k, v in query.items())
        ]

    async def find_one_from_cache(self, value: Any) -> Any:
        results = self.get_items_in_cache(value)
        return results[0] if results else None

    async def find_one_from_db(
        self, param_filter: Mapping[str, Any]
    ) -> Mapping[str, Any]:
        results = await self.get_items_in_db(find_dict=param_filter, to_list=True)
        return results[0] if len(results) >= 1 else None

    async def find_one(
        self, value: Union[Mapping[str, Any], Any], return_first_result: bool = False
    ) -> Any:
        # try to search in cache
        results = self.get_items_in_cache(value)
        if results:
            if len(results[0].get(1, [])) >= 1:
                return results[0].get(1, []) if return_first_result else results

        # if not found in cache, search in database
        results = await self.get_items_in_db(value, to_list=True)
        if results:
            return results[0] if return_first_result else results

        return None  # None if not found

    async def add_to_db(self, data: Mapping[str, Any]) -> None:
        await self.collection.insert_one(data)
        self._add_to_cache(data)

    async def fetch_and_cache_all(self) -> None:
        results = await self.get_items_in_db({}, to_list=True)
        logging.info(f"[{self.name}]: Found {len(results)} items in database")
        for index, data in enumerate(results, start=1):
            self.collection_cache.append(data)

    async def update_db(
        self, data: Mapping[str, Any], new_value: Mapping[str, Any]
    ) -> None:
        await self.collection.update_one(data, {"$set": new_value}, upsert=True)
        old_value = await self.find_one_from_db(data)
        self._update_cache(old_value, new_value)
