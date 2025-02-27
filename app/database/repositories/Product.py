from app.Config import ENV_PROJECT
from app.database.models.Product import product, ProductDB
from .crud.base_mongo_crud import BaseMongoDbCrud
from app.database.repositories.crud.base import PageRequest, Meta, PaginatedResponse
from pydantic import BaseModel
from typing import List


class ProductRepo(BaseMongoDbCrud[ProductDB]):
    def __init__(self):
        super().__init__(
            ENV_PROJECT.MONGO_DATABASE, "Product", unique_attributes=["product_name"]
        )

    async def new(self, sub: product):
        return await self.save(ProductDB(**sub.model_dump()))

    async def viewAllProduct(self, search: str, pagination: PageRequest):
        filter_params = {}
        if search not in ["", None]:
            filter_params["$or"] = [
                {"product_name": {"$regex": search, "$options": "i"}},
                {"category": {"$regex": search, "$options": "i"}},
                {"storage_requirement": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}},
            ]

        pipeline = [
            {"$match": filter_params},
            {"$project": {"created_at": 0, "updated_at": 0}},
            {
                "$facet": {
                    "docs": [
                        {"$skip": (pagination.paging.page - 1) * pagination.paging.limit},
                        {"$limit": pagination.paging.limit},
                        {"$sort": {"expiry_date": 1}},
                    ],
                    "count": [{"$count": "count"}],
                }
            },
        ]

        res = [doc async for doc in self.collection.aggregate(pipeline)]
        docs = res[0]["docs"]
        count = res[0]["count"][0]["count"] if len(res[0]["count"]) > 0 else 0

        return PaginatedResponse(
            docs=docs,
            meta=Meta(
                page=pagination.paging.page,
                limit=pagination.paging.limit,
                total=count,
            ),
        )


product_repo = ProductRepo()
