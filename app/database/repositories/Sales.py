from app.Config import ENV_PROJECT
from .crud.base_mongo_crud import BaseMongoDbCrud
from app.database.models.Sales import Sales, SalesDB
from app.database.repositories.crud.base import (
    PageRequest,
    Meta,
    PaginatedResponse,
    SortingOrder,
    Sort,
    Page,
)

class SalesRepo(BaseMongoDbCrud[SalesDB]):
    def __init__(self):
        super().__init__(
            ENV_PROJECT.MONGO_DATABASE, "Sales", unique_attributes=[]
        )

    async def new(self, sub: Sales):
        return await self.save(
            SalesDB(**sub.model_dump())
        )

    async def get_all_sales(
        self,
        current_user_id: str,
        search: str,
        category: str,
        state: str,
        pagination: PageRequest,
        sort: Sort
    ):
        filter_params = {
            "chemist_id": current_user_id,
        }

        if search not in ["", None]:
            filter_params["$or"] = [
                {"productDetails.product_name": {"$regex": f"^{search}", "$options": "i"}},
                {"productDetails.category": {"$regex": f"^{search}", "$options": "i"}},
            ]

        if category not in ["", None]:
            filter_params["productDetails.category"] = category

        sort_fields_mapping = {
            "product_name": "productDetails.product_name",
            "category": "productDetails.category",
            "state": "productDetails.state",
            "created_at": "created_at",  # Or another field if relevant
        }

        sort_field_mapped = sort_fields_mapping.get(
            sort.sort_field, "productDetails.product_name")
        sort_order_value = 1 if sort.sort_order == SortingOrder.ASC else -1
        sort_criteria = {sort_field_mapped: sort_order_value}

        pipeline=[]
        pipeline=[
            {
                "$match":filter_params
            },
            {
                "$lookup":{
                    "from":"SaleDetails",
                    "localField":"_id",
                    "foreignField":"sale_id",
                    "as":"saleDetails",
                    "pipeline":[
                        {
                            "$project":{
                                "product_id":1,
                                "quantity":1,
                                "unit_price":1,
                            }
                        }
                    ]
                }
            },
            {
                "$unwind":"$saleDetails"
            },
            {
                "$lookup":{
                    "from":"Product",
                    "localField":"saleDetails.product_id",
                    "foreignField": "_id",
                    "as": "productDetails",
                    "pipeline":[
                        {
                            "$project":{
                                "product_name": 1,
                                "category": 1,
                                "state": 1,
                                "measure_of_unit": 1,
                                "no_of_tablets_per_pack": 1,
                                "storage_requirement": 1,
                                "expiry_date": 1,
                                "description": 1,
                                "created_at": 1,
                                "updated_at": 1,
                            }
                        }
                    ]
                }
            },
            {
                "$unwind":"$productDetails"
            },
        ]

        pipeline.append(
            {
                "$facet": {
                    "docs": [
                        {
                            "$skip": (pagination.paging.page - 1) * pagination.paging.limit
                        },
                        {"$limit": pagination.paging.limit},
                    ],
                    "count": [{"$count": "count"}],
                    "unique_categories": [
                        {"$match": {"category": {"$ne": None}}},
                        {"$group": {"_id": "$category"}},
                        {"$project": {"_id": 0, "category": "$_id"}},
                        {"$sort": {"category": 1}}
                    ],
                }
            }
        )

        result = [doc async for doc in self.collection.aggregate(pipeline)]
        res = result[0]

        docs = res["docs"]
        count = res["count"][0]["count"] if len(res["count"]) > 0 else 0
        unique_categories = [entry["category"] for entry in res["unique_categories"]]

        return PaginatedResponse(
            docs=docs,
            meta=Meta(
                **pagination.paging.model_dump(), total=count, unique=unique_categories
            ),
        )

sales_repo = SalesRepo()
