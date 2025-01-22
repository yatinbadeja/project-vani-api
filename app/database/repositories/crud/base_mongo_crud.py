from typing import List

import pymongo
from motor.motor_asyncio import AsyncIOMotorClient

from app.database import mongodb
from app.database.exceptions import DocumentAlreadyExist
from app.database.repositories.crud.base import (
    ID,
    AsyncPagingAndSortingRepository,
    Meta,
    PageRequest,
    PaginatedResponse,
    T,
)


def model_serializer(entity, id):
    result = entity.dict(by_alias=True)
    print("Result : ",result)
    result[id] = str(result[id])
    
    return result


class BaseMongoDbCrud(AsyncPagingAndSortingRepository[T]):

    def __init__(
        self,
        database_name: str,
        collection: str,
        conn: AsyncIOMotorClient = mongodb.client,  # type: ignore
        id: str = "_id",
        default_filter: dict = {},
        unique_attributes: List[str] = [],
    ):
        self.default_filter = default_filter
        self.client: AsyncIOMotorClient = conn  # type: ignore
        self.database_name = database_name
        self.collection_name = collection
        self.collection = self.client[self.database_name][self.collection_name]
        self.id = id
        self.serializer = lambda x: model_serializer(x, self.id)
        self.unique_attributes = unique_attributes
        if self.unique_attributes:
            index_list = [
                (attribute, pymongo.ASCENDING) for attribute in unique_attributes
            ]
            self.collection.create_index(index_list, unique=True)

    async def findOne(
        self, filter: dict, projection: dict = {}, sort: list = [("_id", -1)]
    ) -> T:
        result = await self.collection.find_one(
            {**filter, **self.default_filter}, projection=projection, sort=sort
        )
        return result

    async def findOneById(self, id: ID) -> T:
        result = await self.collection.find_one({self.id: id, **self.default_filter})
        return result

    async def find(self):
        result = await self.collection.find({}, {"_id": 1}).to_list(None)
        ids = []
        for num in result:
            ids.append(num.get("_id"))
        return ids

    async def findAllById(self, ids: List[ID]) -> List[T]:
        cursor = self.collection.find({self.id: {"$in": ids}, **self.default_filter})
        results = []
        async for document in cursor:
            results.append(document)
        return results

    async def exists(self, entity: T) -> bool:
        document = await self.collection.find_one(
            {**entity.dict(by_alias=True), **self.default_filter}
        )
        return document is not None

    async def existsByQuery(self, query: dict) -> bool:
        document = await self.collection.find_one({**query, **self.default_filter})
        return document is not None

    async def existsById(self, id: ID) -> bool:
        document = await self.collection.find_one({self.id: id, **self.default_filter})
        return document is not None

    async def count(self, filter: dict) -> int:
        return await self.collection.count_documents({**filter, **self.default_filter})

    async def delete(self, entity: T) -> bool:
        entity = entity.dict(by_alias=True)
        filter_ = {self.id: entity["_id"], **self.default_filter}
        result = self.collection.delete_one(filter_)
        return result.deleted_count

    async def deleteOne(self, filter: dict):
        result = await self.collection.delete_one({**filter, **self.default_filter})
        return result

    async def deleteById(self, id: ID) -> bool:
        filter_ = {self.id: id, **self.default_filter}
        result = await self.collection.delete_one(filter_)
        return result.deleted_count

    async def deleteAll(self, filter: dict):
        result = await self.collection.delete_many({**filter, **self.default_filter})
        return result.deleted_count

    async def deleteAllById(self, ids: List[ID]) -> bool:
        filter_ = {self.id: {"$in": ids}, **self.default_filter}
        result = await self.collection.delete_many(filter_)
        return result.deleted_count == len(ids)

    async def replace(self, entity: T) -> T:
        entity = entity.dict(by_alias=True)
        result = await self.collection.replace_one(
            {self.id: entity["_id"]}, entity, upsert=False
        )
        if result.matched_count == 0:
            raise ValueError("No document found to replace")
        return entity

    async def save(self, entity: T) -> T:
        item = self.serializer(entity)
        if await self.existsById(item[self.id]):
            raise DocumentAlreadyExist(f"Document with ID {self.id} already exist")
        await self.collection.insert_one(item)
        return entity

    async def findAll(
        self, filter: dict, pagination: PageRequest, projection: dict = {}
    ) -> PaginatedResponse:
        agg_query = [
            {"$match": {**filter, **self.default_filter}},
            {
                "$lookup": {
                    "from": "token",
                    "localField": "_id",
                    "foreignField": "user_id",
                    "as": "token_data",
                }
            },
            {
                "$addFields": {
                    "token_data": {
                        "$cond": {
                            "if": {"$eq": [{"$size": "$token_data"}, 0]},
                            "then": [{"updated_at": ""}],
                            "else": "$token_data",
                        }
                    }
                }
            },
            {"$unwind": "$token_data"},
            {
                "$group": {
                    "_id": "$_id",
                    "Details": {"$first": "$$ROOT"},
                    "lastLogin": {"$max": "$token_data.updated_at"},
                }
            },
            {
                "$replaceRoot": {
                    "newRoot": {
                        "$mergeObjects": ["$Details", {"lastLogin": "$lastLogin"}]
                    }
                }
            },
        ]

        if projection:
            agg_query.append({"$project": projection})

        agg_query.append(
            {
                "$facet": {
                    "docs": [
                        {
                            "$sort": {
                                pagination.sorting.sort_field: int(
                                    pagination.sorting.sort_order.value
                                )
                            }
                        },
                        {"$skip": (pagination.paging.page - 1) * pagination.paging.limit},
                        {"$limit": pagination.paging.limit},
                    ],
                    "count": [{"$count": "count"}],
                }
            }
        )
        res = [doc async for doc in self.collection.aggregate(agg_query)]
        docs = res[0]["docs"]
        count = res[0]["count"][0]["count"] if len(res[0]["count"]) > 0 else 0
        return PaginatedResponse(
            docs=docs, meta=Meta(**pagination.paging.model_dump(), total=count)
        )

    async def update_one(self, filter: dict, update: dict):
        return await self.collection.update_one(filter, update)

    async def filterByName(self, name: str):
        await self.collection.find_one({"name": {"$regex": name}})
