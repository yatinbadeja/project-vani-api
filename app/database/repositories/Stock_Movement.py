from app.Config import ENV_PROJECT
from .crud.base_mongo_crud import BaseMongoDbCrud
from app.database.models.Stock_Movement import StockMovement, StockMovementDB
from app.database.models.Order_Details import OrderDetails
from app.schema.enums import StockMovementTypeEnum
from typing import List
from app.database.repositories.Product_Stock import product_stock_repo
from pymongo import UpdateOne
from app.database.models.Product_Stock import ProductStock, ProductStockDB
from app.database.models.Order_Details import Orders
from app.database.repositories.crud.base import (
    PageRequest,
    Meta,
    PaginatedResponse,
    SortingOrder,
    Sort,
    Page,
)

class StockMovementRepo(BaseMongoDbCrud):
    def __init__(self):
        super().__init__(
            ENV_PROJECT.MONGO_DATABASE, "StockMovement", unique_attributes=[]
        )

    async def new(self, sub:StockMovement):
        return await self.save(
            StockMovementDB(**sub.model_dump())
        )
    
    async def insert_many(self, stock_movements: List[StockMovementDB]):
        documents = [
            {**doc.model_dump(), "_id": str(doc.stock_movement_id)}
            for doc in stock_movements
        ]
        return await self.collection.insert_many(documents)
    
    async def update_incoming_stock(self, orders: List[Orders], chemist_id: str):
        """
        Updates product details in stock movement and available-quantity in productStock by mapping each element and creating multiple entries
        with movement_type as IN for each product.
        """
        stock_movements= []
        bulk_update_operations = []
        product_stock_entries_to_insert= []

        print("order_details", orders)

        for order in orders:
            product_id = order.product_id
            quantity = order.quantity
            unit_price = order.unit_price

            stock_movement = StockMovementDB(
                product_id=order.product_id,
                quantity=order.quantity,
                movement_type=StockMovementTypeEnum.IN,
                chemist_id=chemist_id,
                unit_price=order.unit_price
            )
            stock_movements.append(stock_movement)

            # Check if the product already exists in ProductStock associated with chemist_id
            existing_product_stock = await product_stock_repo.findOne({
                "product_id" : product_id, 
                "chemist_id" : chemist_id
            })
            if existing_product_stock:
                if isinstance(existing_product_stock, dict):
                    existing_product_stock = ProductStockDB.parse_obj(existing_product_stock)
                    
                new_quantity = existing_product_stock.available_quantity + quantity
                bulk_update_operations.append(
                    UpdateOne(
                        {"product_stock_id": existing_product_stock.product_stock_id},
                        {"$set": {"available_quantity": new_quantity}}
                    )
                )
            else:
                product_stock_entries_to_insert.append(
                    ProductStockDB(
                        product_id=product_id,
                        available_quantity=quantity,
                        chemist_id=chemist_id
                    )
                )

        if stock_movements:
            await self.insert_many(stock_movements)
        
        if bulk_update_operations:
            print("bulk_update_operations",bulk_update_operations)
            await product_stock_repo.bulk_write(bulk_update_operations)
        
        if product_stock_entries_to_insert:
            print("product_stock_entries_to_insert",product_stock_entries_to_insert)
            await product_stock_repo.insert_many(product_stock_entries_to_insert)

        return {"message": "Stock and product stock updated successfully"}

    async def get_all_Stock_movement(
            self,
            current_user_id: str,
            search: str,
            category: str,
            state:str,
            movement_type:str,
            pagination: PageRequest,
            sort: Sort
    ):
        filter_params = {
            "chemist_id": current_user_id,
        }

        if movement_type not in ["", None]:
            filter_params["movement_type"] = movement_type

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

        pipeline = []
        pipeline = [
            {
                "$match": filter_params
            },
            {
                "$lookup": {
                    "from": "Product",
                    "localField": "product_id",
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
                "$unwind": {
                    "path": "$productDetails",
                    "preserveNullAndEmptyArrays": True
                }
            },
            {
                "$project": {
                    "product_id": 1,
                    "quantity": 1,
                    "movement_type": 1,
                    "unit_price": 1,
                    "created_at": 1,
                    "productDetails": {
                        "product_name": "$productDetails.product_name",
                        "category": "$productDetails.category",
                        "state": "$productDetails.state",
                        "measure_of_unit": "$productDetails.measure_of_unit",
                        "no_of_tablets_per_pack": "$productDetails.no_of_tablets_per_pack",
                        "storage_requirement": "$productDetails.storage_requirement",
                        "expiry_date": "$productDetails.expiry_date",
                        "description": "$productDetails.description",
                        # "created_at": "$productDetails.created_at",
                        # "updated_at": "$productDetails.updated_at"
                    }
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
        
stock_movement_repo = StockMovementRepo()