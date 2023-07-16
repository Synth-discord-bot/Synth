import asyncio
from typing import Any, Mapping, Union, List

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCursor

_client = AsyncIOMotorClient("mongodb://127.0.0.1:27017")
database = _client["synth"]


class BaseDatabase:
    def __init__(self, database_name: str) -> None:
        self.collection = database[database_name]
        self.collection_cache = {}

    async def get_items_in_db(
            self, find_dict: Mapping[str, Any],
            to_list: bool = True,
            count: Union[int, None] = None
    ) -> Union[List[Mapping[str, Any]], AsyncIOMotorCursor]:
        result = self.collection.find(filter=find_dict)
        if to_list:
            return await result.to_list(length=count)

        return result

    def get_items_in_cache(self, query: Any) -> List[Any]:
        # print(self.collection_cache)
        # for index, res in enumerate(self.collection_cache):
        #     # print(index, bool(self.collection_cache.get(value)))
        #     print(value.items())
        #     print(index, bool(self.collection_cache.get(frozenset(value.items()))))
        # results = [res for index, res in enumerate(self.collection_cache) if res[index] in value]
        # return results
        # print(value.items())
        # find_key, find_value = value.keys(), value.values()
        # return next((
        #     key for key, value in self.collection_cache.items()
        #     if isinstance(value, dict) and find_key in value and value[find_value] == find_value),
        #     None
        # )
        return [{key: value} for key, value in self.collection_cache.items() if
                all(k in value and value[k] == v for k, v in query.items())]
        # return next(((key, value) for key, value in data.items() if
        #              all(k in value and value[k] == v for k, v in query.items())), None)

    # def find_in_dict(self, query):
    #     return [(key, value) for key, value in self.collection_cache.items() if
    #             all(k in value and value[k] == v for k, v in query.items())]

    async def find_one_from_cache(self, value: Any) -> Any:
        results = self.get_items_in_cache(value)
        if len(results) > 0:
            return results[0]
        return None

    async def find_one_from_db(self, param_filter: Mapping[str, Any]) -> Any:
        results = await self.get_items_in_db(find_dict=param_filter, to_list=True)
        if len(results) > 0:
            return results[0]
        return None

    async def find_one_cache(self, value: Any) -> Any:
        results = self.get_items_in_cache(value)
        if len(results) > 0:
            return results[0]
        return None

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

    async def add_to_db(self, data: Mapping[str, Any]) -> None:
        await self.collection.insert_one(data)
        self._add_to_cache(data)

    async def fetch_and_cache_all(self) -> None:
        results = await self.get_items_in_db({}, to_list=True)
        print(results)
        for index, data in enumerate(results, start=1):
            self.collection_cache[index] = data
