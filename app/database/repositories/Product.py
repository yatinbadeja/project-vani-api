from app.Config import ENV_PROJECT
from app.database.models.Product import product, ProductDB
from .crud.base_mongo_crud import BaseMongoDbCrud
from app.database.repositories.crud.base import (
    PageRequest,
    Meta,
    PaginatedResponse,
    SortingOrder,
    Sort,
    Page,
)
from pydantic import BaseModel
from typing import List


class ProductRepo(BaseMongoDbCrud[ProductDB]):
    def __init__(self):
        super().__init__(
            ENV_PROJECT.MONGO_DATABASE, "Product", unique_attributes=["product_name"]
        )

    async def new(self, sub: product):
        return await self.save(ProductDB(**sub.model_dump()))

    async def viewAllProduct(
        self, search: str, category: str, pagination: PageRequest, sort: Sort
    ):
        filter_params = {}
        if search not in ["", None]:
            filter_params["$or"] = [
                {"product_name": {"$regex": search, "$options": "i"}},
                {"category": {"$regex": search, "$options": "i"}},
                {"storage_requirement": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}},
            ]
        if category not in ["", None]:
            filter_params["category"] = category

        # Define sorting logic
        sort_options = {
            "name_asc": {"product_name": 1},
            "name_desc": {"product_name": -1},
            "price_asc": {"price": 1},
            "price_desc": {"price": -1},
            "expiry_asc": {"expiry_date": 1},
            "expiry_desc": {"expiry_date": -1},
            "created_at_asc": {"created_at": 1},
            "created_at_desc": {"created_at": -1},
        }

        # Construct sorting key
        sort_key = f"{sort.sort_field}_{'asc' if sort.sort_order == SortingOrder.ASC else 'desc'}"

        sort_stage = sort_options.get(sort_key, {"expiry_date": 1})
        print("sort.sort_field", sort.sort_field)
        print("sort.sort_order", sort.sort_order)
        print("sort_stage", sort_stage)
        print("sort_key", sort_key)

        pipeline = [
            {"$match": filter_params},
            {"$sort": sort_stage},
            {"$project": {"created_at": 0, "updated_at": 0}},
            {
                "$facet": {
                    "docs": [
                        {"$skip": (pagination.paging.page - 1) * pagination.paging.limit},
                        {"$limit": pagination.paging.limit},
                    ],
                    "count": [{"$count": "count"}],
                }
            },
        ]

        unique_categories_pipeline = [
            {"$group": {"_id": "$category"}},
            {"$project": {"_id": 0, "category": "$_id"}},
            {"$sort": {"category": 1}},
        ]

        res = [doc async for doc in self.collection.aggregate(pipeline)]
        categories_res = [
            doc async for doc in self.collection.aggregate(unique_categories_pipeline)
        ]
        docs = res[0]["docs"]
        count = res[0]["count"][0]["count"] if len(res[0]["count"]) > 0 else 0
        unique_categories = [entry["category"] for entry in categories_res]

        return PaginatedResponse(
            docs=docs,
            meta=Meta(
                page=pagination.paging.page,
                limit=pagination.paging.limit,
                total=count,
                unique=unique_categories,
            ),
        )


product_repo = ProductRepo()
