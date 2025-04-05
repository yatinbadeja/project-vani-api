from app.Config import ENV_PROJECT
from app.database.models.Chemist import Chemist, ChemistDB
from .crud.base_mongo_crud import BaseMongoDbCrud
from app.database.models.Orders import OrderStatus
from app.database.repositories.crud.base import (
    PageRequest,
    Meta,
    PaginatedResponse,
    SortingOrder,
    Sort,
    Page,
)
class ChemistRepo(BaseMongoDbCrud[ChemistDB]):
    def __init__(self):
        super().__init__(
            ENV_PROJECT.MONGO_DATABASE, "Chemist", unique_attributes=[]
        )

    async def new(self, sub: Chemist):
        return await self.save(
            ChemistDB(**sub.model_dump())
        )
    
    async def viewWareHouseInventory(
            self,
            current_user_id: str,
            search:str,
            category:str,
            pagination: PageRequest,
            sort: Sort
    ) : 
        filter_params = {
            "user_id": current_user_id,
        }

        if search not in ["", None]:
            filter_params["$or"] = [
                {"product_name": {"$regex": f"^{search}", "$options": "i"}},
                {"category": {"$regex": f"^{search}", "$options": "i"}},
            ]
        
        if category not in ["", None]:
            filter_params["category"] = category

        sort_fields_mapping = {
            "product_name": "productDetails.product_name",
            "category": "productDetails.category",
            "state": "productDetails.state",
            "created_at": "created_at",  # Or another field if relevant
        }
        
        sort_field_mapped = sort_fields_mapping.get(sort.sort_field, "productDetails.product_name")
        sort_order_value = 1 if sort.sort_order == SortingOrder.ASC else -1
        sort_criteria = {sort_field_mapped: sort_order_value}

        pipeline=[]
        pipeline= [
            {"$match": filter_params},
            {
                "$lookup": {
                    "from": "Orders",
                    "localField": "_id",
                    "foreignField": "chemist_id",
                    "as": "ordersList",
                    "pipeline": [
                        {
                            "$match": {
                                "status": OrderStatus.SHIPPED
                            }
                        }
                    ]
                }
            },
            {
                "$lookup": {
                    "from": "OrderDetails",
                    "localField": "ordersList._id",
                    "foreignField": "order_id",
                    "as": "orderDetailsList"
                }
            },
            {
                "$unwind": "$orderDetailsList"
            },
            {
                "$unwind": "$orderDetailsList.product_details"
            },
            {
                "$group": {
                    "_id": "$orderDetailsList.product_details.product_id",
                    "quantity": {"$sum": "$orderDetailsList.product_details.quantity"},
                    "purchasing_price": {
                        "$sum": {
                            "$multiply": ["$orderDetailsList.product_details.unit_price", "$orderDetailsList.product_details.quantity"]
                        }
                    },
                    "category": {"$first": "$orderDetailsList.product_details.category"}
                }
            },
            {
                "$lookup": {
                    "from": "Product",
                    "localField": "_id",
                    "foreignField": "_id",
                    "as": "productDetails",
                    "pipeline": [
                        {
                            "$project": {
                                "product_name": 1,
                                "category": 1,
                                "state": 1,
                                "measure_of_unit": 1,
                                "no_of_tablets_per_pack": 1,
                                "storage_requirement": 1,
                            }
                        }
                    ]
                }
            },
            {
                "$unwind": "$productDetails"
            },
            {
                '$project': {
                    "_id": 1,
                    "quantity": 1,
                    "purchasing_price": 1,
                    "product_name": "$productDetails.product_name",
                    "category": "$productDetails.category",
                    "state": "$productDetails.state",
                    "measure_of_unit": "$productDetails.measure_of_unit",
                    "no_of_tablets_per_pack": "$productDetails.no_of_tablets_per_pack",
                    "storage_requirement": "$productDetails.storage_requirement",
                }
            },
            {"$sort": sort_criteria},
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

chemist_repo = ChemistRepo()
