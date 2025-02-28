from app.Config import ENV_PROJECT
from app.database.models.user import User, UserDB
from .crud.base_mongo_crud import BaseMongoDbCrud
from app.database.repositories.crud.base import (
    PageRequest,
    Meta,
    PaginatedResponse,
    Sort,
    SortingOrder,
)


class userRepo(BaseMongoDbCrud[UserDB]):
    def __init__(self):
        super().__init__(ENV_PROJECT.MONGO_DATABASE, "User", unique_attributes=["email"])

    async def new(self, sub: User):
        return await self.save(UserDB(**sub.model_dump()))

    async def viewAllStockist(
        self,
        search: str,
        state: str,
        pagination: PageRequest,
        sort: Sort,
    ):
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
                {"StockistData.address.city": {"$regex": f"^{search}", "$options": "i"}},
            ]
        if state not in ["", None]:
            filter_params["StockistData.address.state"] = state

        sort_fields_mapping = {
            "name": "StockistData.name.first_name",
            "company_name": "StockistData.company_name",
            "city": "StockistData.address.city",
            "state": "StockistData.address.state",
            "created_at": "created_at",
        }

        sort_field_mapped = sort_fields_mapping.get(
            sort.sort_field, "StockistData.name.first_name"
        )
        sort_order_value = 1 if sort.sort_order == SortingOrder.ASC else -1
        sort_criteria = {sort_field_mapped: sort_order_value}

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
                {"$sort": sort_criteria},
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
            {"$sort": {"state": 1}},
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
                **pagination.paging.model_dump(), total=count, unique=unique_states
            ),
        )

    async def viewAllChemist(
        self,
        search: str,
        state: str,
        pagination: PageRequest,
        sort: Sort,
    ):
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
                {"ChemistData.address.city": {"$regex": f"^{search}", "$options": "i"}},
            ]
        if state not in ["", None]:
            filter_params["ChemistData.address.state"] = state

        sort_fields_mapping = {
            "name": "ChemistData.name.first_name",
            "shop_name": "ChemistData.shop_name",
            "city": "ChemistData.address.city",
            "state": "ChemistData.address.state",
            "created_at": "created_at",
        }

        sort_field_mapped = sort_fields_mapping.get(
            sort.sort_field, "ChemistData.name.first_name"
        )
        sort_order_value = 1 if sort.sort_order == SortingOrder.ASC else -1
        sort_criteria = {sort_field_mapped: sort_order_value}

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
                {"$sort": sort_criteria},
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
            {"$sort": {"state": 1}},
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
                **pagination.paging.model_dump(), total=count, unique=unique_states
            ),
        )

    # async def viewAllChemist(
    #     self,
    #     search: str,
    #     state: str,
    #     pagination: PageRequest,
    #     sort: Sort,
    # ):
    #     filter_params = {}
    #     if search not in ["", None]:
    #         filter_params["$or"] = [
    #             {"email": {"$regex": f"^{search}", "$options": "i"}},
    #             {
    #                 "ChemistData.name.first_name": {
    #                     "$regex": f"^{search}",
    #                     "$options": "i",
    #                 }
    #             },
    #             {
    #                 "ChemistData.name.middle_name": {
    #                     "$regex": f"^{search}",
    #                     "$options": "i",
    #                 }
    #             },
    #             {"ChemistData.name.last_name": {"$regex": f"^{search}", "$options": "i"}},
    #             {"ChemistData.shop_name": {"$regex": f"^{search}", "$options": "i"}},
    #         ]
    #     if state not in ["", None]:
    #         filter_params["ChemistData.address.state"] = state

    #     sort_fields_mapping = {
    #         "name": "ChemistData.name.first_name",
    #         "shop_name": "ChemistData.shop_name",
    #         "city": "ChemistData.address.city",
    #         "state": "ChemistData.address.state",
    #         "created_at": "created_at",
    #     }

    #     sort_order_value = 1 if sort_order == "asc" else -1
    #     sort_criteria = {
    #         sort_fields_mapping.get(
    #             sort_field, "ChemistData.name.first_name"
    #         ): sort_order_value
    #     }

    #     pipeline = [
    #         {"$match": {"role": "Chemist"}},
    #         {"$project": {"password": 0, "created_at": 0, "updated_at": 0}},
    #         {
    #             "$lookup": {
    #                 "from": "Chemist",
    #                 "localField": "_id",
    #                 "foreignField": "user_id",
    #                 "as": "ChemistData",
    #             }
    #         },
    #         {
    #             "$set": {
    #                 "ChemistData": {
    #                     "$ifNull": [{"$arrayElemAt": ["$ChemistData", 0]}, None]
    #                 }
    #             }
    #         },
    #         {
    #             "$project": {
    #                 "ChemistData._id": 0,
    #                 "ChemistData.user_id": 0,
    #                 "ChemistData.created_at": 0,
    #                 "ChemistData.updated_at": 0,
    #             }
    #         },
    #         {"$match": filter_params},
    #         {"$sort": sort_criteria},  # <-- Move sorting here
    #         {
    #             "$facet": {
    #                 "docs": [
    #                     {"$skip": (pagination.paging.page - 1) * pagination.paging.limit},
    #                     {"$limit": pagination.paging.limit},
    #                 ],
    #                 "count": [{"$count": "count"}],
    #             }
    #         },
    #     ]

    #     unique_states_pipeline = [
    #         {"$match": {"role": "Chemist"}},
    #         {
    #             "$lookup": {
    #                 "from": "Chemist",
    #                 "localField": "_id",
    #                 "foreignField": "user_id",
    #                 "as": "ChemistData",
    #             }
    #         },
    #         {
    #             "$set": {
    #                 "ChemistData": {
    #                     "$ifNull": [{"$arrayElemAt": ["$ChemistData", 0]}, None]
    #                 }
    #             }
    #         },
    #         {"$group": {"_id": "$ChemistData.address.state"}},
    #         {"$project": {"_id": 0, "state": "$_id"}},
    #         {"$sort": {"state": 1}},
    #     ]

    #     res = [doc async for doc in self.collection.aggregate(pipeline)]
    #     states_res = [
    #         doc async for doc in self.collection.aggregate(unique_states_pipeline)
    #     ]

    #     docs = res[0]["docs"]
    #     count = res[0]["count"][0]["count"] if len(res[0]["count"]) > 0 else 0
    #     unique_states = [entry["state"] for entry in states_res]

    #     return PaginatedResponse(
    #         docs=docs,
    #         meta=Meta(
    #             **pagination.paging.model_dump(), total=count, unique_states=unique_states
    #         ),
    #     )


user_repo = userRepo()
