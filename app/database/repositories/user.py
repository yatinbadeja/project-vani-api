from app.Config import ENV_PROJECT
from app.database.models.user import User, UserDB
from .crud.base_mongo_crud import BaseMongoDbCrud
from app.database.repositories.crud.base import PageRequest, Meta, PaginatedResponse
from app.schema.enums import UserRole
from typing import Optional


class userRepo(BaseMongoDbCrud[UserDB]):
    def __init__(self):
        super().__init__(ENV_PROJECT.MONGO_DATABASE, "User", unique_attributes=["email"])

    async def new(self, sub: User):
        return await self.save(UserDB(**sub.model_dump()))

    async def viewAllStockist(self, search: str, state: str, pagination: PageRequest):
        filter_params = {}
        if search not in ["", None]:
            filter_params["$or"] = [
                {"email": {"$regex": f"^{search}", "$options": "i"}},
                {
                    "StockistData.name.first_name": {
                        "$regex": f"^{search}",
                        "$options": "i",
                    }
                },
                {
                    "StockistData.name.middle_name": {
                        "$regex": f"^{search}",
                        "$options": "i",
                    }
                },
                {
                    "StockistData.name.last_name": {
                        "$regex": f"^{search}",
                        "$options": "i",
                    }
                },
                {"StockistData.company_name": {"$regex": f"^{search}", "$options": "i"}},
            ]
        if state not in ["", None]:
            filter_params["ChemistData.address.state"] = state

        pipeline = []
        pipeline.extend(
            [
                {"$match": {"role": "Stockist"}},
                {"$project": {"password": 0, "created_at": 0, "updated_at": 0}},
                {
                    "$lookup": {
                        "from": "Stockist",
                        "localField": "_id",
                        "foreignField": "user_id",
                        "as": "StockistData",
                    }
                },
                {
                    "$set": {
                        "StockistData": {
                            "$ifNull": [{"$arrayElemAt": ["$StockistData", 0]}, None]
                        }
                    }
                },
                {
                    "$project": {
                        "StockistData._id": 0,
                        "StockistData.user_id": 0,
                        "StockistData.created_at": 0,
                        "StockistData.updated_at": 0,
                    }
                },
                {"$match": filter_params},
            ]
        )

        pipeline.append(
            {
                "$facet": {
                    "docs": [
                        {
                            "$skip": (pagination.paging.page - 1)
                            * (pagination.paging.limit)
                        },
                        {"$limit": pagination.paging.limit},
                        {"$sort": {"date": 1, "hour": 1, "minute": 1}},
                    ],
                    "count": [{"$count": "count"}],
                }
            }
        )

        unique_states_pipeline = [
            {"$match": {"role": "Stockist"}},
            {
                "$lookup": {
                    "from": "Stockist",
                    "localField": "_id",
                    "foreignField": "user_id",
                    "as": "StockistData",
                }
            },
            {
                "$set": {
                    "StockistData": {
                        "$ifNull": [{"$arrayElemAt": ["$StockistData", 0]}, None]
                    }
                }
            },
            {"$group": {"_id": "$StockistData.address.state"}},
            {"$project": {"_id": 0, "state": "$_id"}},
        ]
        res = [doc async for doc in self.collection.aggregate(pipeline)]
        states_res = [
            doc async for doc in self.collection.aggregate(unique_states_pipeline)
        ]
        docs = res[0]["docs"]
        count = res[0]["count"][0]["count"] if len(res[0]["count"]) > 0 else 0
        unique_states = [entry["state"] for entry in states_res]

        return PaginatedResponse(
            docs=docs,
            meta=Meta(
                **pagination.paging.model_dump(), total=count, unique_states=unique_states
            ),
        )

    async def viewAllChemist(self, search: str, state: str, pagination: PageRequest):
        filter_params = {}
        if search not in ["", None]:
            filter_params["$or"] = [
                {"email": {"$regex": f"^{search}", "$options": "i"}},
                {
                    "ChemistData.name.first_name": {
                        "$regex": f"^{search}",
                        "$options": "i",
                    }
                },
                {
                    "ChemistData.name.middle_name": {
                        "$regex": f"^{search}",
                        "$options": "i",
                    }
                },
                {"ChemistData.name.last_name": {"$regex": f"^{search}", "$options": "i"}},
                {"ChemistData.shop_name": {"$regex": f"^{search}", "$options": "i"}},
            ]
        if state not in ["", None]:
            filter_params["ChemistData.address.state"] = state

        pipeline = []
        pipeline.extend(
            [
                {"$match": {"role": "Chemist"}},
                {"$project": {"password": 0, "created_at": 0, "updated_at": 0}},
                {
                    "$lookup": {
                        "from": "Chemist",
                        "localField": "_id",
                        "foreignField": "user_id",
                        "as": "ChemistData",
                    }
                },
                {
                    "$set": {
                        "ChemistData": {
                            "$ifNull": [{"$arrayElemAt": ["$ChemistData", 0]}, None]
                        }
                    }
                },
                {
                    "$project": {
                        "ChemistData._id": 0,
                        "ChemistData.user_id": 0,
                        "ChemistData.created_at": 0,
                        "ChemistData.updated_at": 0,
                    }
                },
                {"$match": filter_params},
            ]
        )

        pipeline.append(
            {
                "$facet": {
                    "docs": [
                        {
                            "$skip": (pagination.paging.page - 1)
                            * (pagination.paging.limit)
                        },
                        {"$limit": pagination.paging.limit},
                        {"$sort": {"date": 1, "hour": 1, "minute": 1}},
                    ],
                    "count": [{"$count": "count"}],
                }
            }
        )

        unique_states_pipeline = [
            {"$match": {"role": "Chemist"}},
            {
                "$lookup": {
                    "from": "Chemist",
                    "localField": "_id",
                    "foreignField": "user_id",
                    "as": "ChemistData",
                }
            },
            {
                "$set": {
                    "ChemistData": {
                        "$ifNull": [{"$arrayElemAt": ["$ChemistData", 0]}, None]
                    }
                }
            },
            {"$group": {"_id": "$ChemistData.address.state"}},
            {"$project": {"_id": 0, "state": "$_id"}},
        ]

        res = [doc async for doc in self.collection.aggregate(pipeline)]
        states_res = [
            doc async for doc in self.collection.aggregate(unique_states_pipeline)
        ]

        docs = res[0]["docs"]
        count = res[0]["count"][0]["count"] if len(res[0]["count"]) > 0 else 0
        unique_states = [entry["state"] for entry in states_res]

        return PaginatedResponse(
            docs=docs,
            meta=Meta(
                **pagination.paging.model_dump(), total=count, unique_states=unique_states
            ),
        )


user_repo = userRepo()
