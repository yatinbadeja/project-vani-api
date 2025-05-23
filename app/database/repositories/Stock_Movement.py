from app.Config import ENV_PROJECT
from .crud.base_mongo_crud import BaseMongoDbCrud
from app.database.models.Stock_Movement import StockMovement, StockMovementDB
from app.database.models.Order_Details import OrderDetails
from app.schema.enums import StockMovementTypeEnum
from typing import List, Union
from app.database.repositories.Product_Stock import product_stock_repo
from pymongo import UpdateOne
from app.database.models.Product_Stock import ProductStock, ProductStockDB
from app.database.models.Order_Details import Orders
from datetime import datetime
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

    async def new(self, sub: StockMovement):
        return await self.save(StockMovementDB(**sub.model_dump()))

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
        stock_movements = []
        bulk_update_operations = []
        product_stock_entries_to_insert = []

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
                unit_price=order.unit_price,
            )
            stock_movements.append(stock_movement)

            # Check if the product already exists in ProductStock associated with chemist_id
            existing_product_stock = await product_stock_repo.findOne(
                {"product_id": product_id, "chemist_id": chemist_id}
            )
            if existing_product_stock:
                if isinstance(existing_product_stock, dict):
                    existing_product_stock = ProductStockDB.parse_obj(
                        existing_product_stock
                    )

                new_quantity = existing_product_stock.available_quantity + quantity
                bulk_update_operations.append(
                    UpdateOne(
                        {"product_stock_id": existing_product_stock.product_stock_id},
                        {"$set": {"available_quantity": new_quantity}},
                    )
                )
            else:
                product_stock_entries_to_insert.append(
                    ProductStockDB(
                        product_id=product_id,
                        available_quantity=quantity,
                        chemist_id=chemist_id,
                    )
                )

        if stock_movements:
            await self.insert_many(stock_movements)

        if bulk_update_operations:
            print("bulk_update_operations", bulk_update_operations)
            await product_stock_repo.bulk_write(bulk_update_operations)

        if product_stock_entries_to_insert:
            print("product_stock_entries_to_insert", product_stock_entries_to_insert)
            await product_stock_repo.insert_many(product_stock_entries_to_insert)

        return {"message": "Stock and product stock updated successfully"}

    async def get_all_Stock_movement(
        self,
        current_user_id: str,
        search: str,
        category: str,
        state: str,
        movement_type: str,
        startDate: str,
        endDate: str,
        pagination: PageRequest,
        sort: Sort,
    ):
        filter_params = {}

        if search not in ["", None]:
            filter_params["$or"] = [
                {
                    "productDetails.product_name": {
                        "$regex": f"^{search}",
                        "$options": "i",
                    }
                },
                {"productDetails.category": {"$regex": f"^{search}", "$options": "i"}},
                {"productDetails.description": {"$regex": f"^{search}", "$options": "i"}},
                {"productDetails.state": {"$regex": f"^{search}", "$options": "i"}},
                {
                    "productDetails.storage_requirement": {
                        "$regex": f"^{search}",
                        "$options": "i",
                    }
                },
            ]

        if movement_type not in ["", None]:
            filter_params["movement_type"] = movement_type

        if category not in ["", None]:
            filter_params["productDetails.category"] = category

        if state not in ["", None]:
            filter_params["productDetails.state"] = state

        if startDate not in ["", None] and endDate not in ["", None]:
            try:
                start_date = (
                    datetime.fromisoformat(startDate.replace("Z", "+00:00"))
                    if "T" in startDate
                    else datetime.strptime(startDate, "%Y-%m-%d")
                )
                end_date = (
                    datetime.fromisoformat(endDate.replace("Z", "+00:00"))
                    if "T" in endDate
                    else datetime.strptime(endDate, "%Y-%m-%d")
                )
                if "T" not in endDate:
                    end_date = end_date.replace(
                        hour=23, minute=59, second=59, microsecond=999999
                    )

                filter_params["created_at"] = {"$gte": start_date, "$lte": end_date}
            except ValueError:
                filter_params["created_at"] = {"$gte": startDate, "$lte": endDate}

        sort_fields_mapping = {
            "product_name": "productDetails.product_name",
            "category": "productDetails.category",
            "state": "productDetails.state",
            "created_at": "created_at",  # Or another field if relevant
        }

        sort_field_mapped = sort_fields_mapping.get(
            sort.sort_field, "productDetails.product_name"
        )
        sort_order_value = 1 if sort.sort_order == SortingOrder.ASC else -1
        sort_criteria = {sort_field_mapped: sort_order_value}

        pipeline = []
        pipeline = [
            {"$match": {"chemist_id": current_user_id}},
            {
                "$lookup": {
                    "from": "Product",
                    "localField": "product_id",
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
                                "expiry_date": 1,
                                "description": 1,
                                "created_at": 1,
                                "updated_at": 1,
                            }
                        }
                    ],
                }
            },
            {"$unwind": {"path": "$productDetails", "preserveNullAndEmptyArrays": True}},
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
                    },
                }
            },
            {"$match": filter_params},
            {"$sort": sort_criteria},
        ]

        pipeline.append(
            {
                "$facet": {
                    "docs": [
                        {"$skip": (pagination.paging.page - 1) * pagination.paging.limit},
                        {"$limit": pagination.paging.limit},
                    ],
                    "count": [{"$count": "count"}],
                }
            }
        )

        unique_categories_pipeline = [
            {"$match": {"chemist_id": current_user_id}},
            {
                "$lookup": {
                    "from": "Product",
                    "localField": "product_id",
                    "foreignField": "_id",
                    "as": "productDetails",
                    "pipeline": [
                        {
                            "$project": {
                                "category": 1,
                            }
                        }
                    ],
                }
            },
            {"$unwind": {"path": "$productDetails", "preserveNullAndEmptyArrays": True}},
            {"$group": {"_id": "$productDetails.category"}},
            {"$project": {"_id": 0, "category": "$_id"}},
            {"$sort": {"category": 1}},
        ]
        result = [doc async for doc in self.collection.aggregate(pipeline)]
        categories_res = [
            doc async for doc in self.collection.aggregate(unique_categories_pipeline)
        ]
        res = result[0]

        docs = res["docs"]
        count = res["count"][0]["count"] if len(res["count"]) > 0 else 0
        unique_categories = [entry["category"] for entry in categories_res]

        return PaginatedResponse(
            docs=docs,
            meta=Meta(
                **pagination.paging.model_dump(), total=count, unique=unique_categories
            ),
        )

    async def get_total_sales(self, chemist_id: str, movement: str):
        pipeline = (
            [{"$match": {"chemist_id": chemist_id, "movement_type": movement}}]
            if chemist_id != ""
            else []
        )
        pipeline.extend(
            [
                {"$set": {"amount": {"$multiply": ["$quantity", "$unit_price"]}}},
                {"$group": {"_id": "$id", "total_amount": {"$sum": "$amount"}}},
            ]
        )
        return await self.collection.aggregate(pipeline=pipeline).to_list(None)

    async def get_total_sales_chemist_wise(self, chemist_id: str, movement: str):

        pipeline = []

        if chemist_id == "":
            pipeline.append({"$match": {"movement_type": movement}})
            group_id = "$chemist_id"
        else:
            pipeline.append(
                {"$match": {"chemist_id": chemist_id, "movement_type": movement}}
            )
            group_id = None  # Single chemist total

        pipeline.extend(
            [
                {
                    "$lookup": {
                        "from": "Chemist",
                        "localField": "chemist_id",
                        "foreignField": "user_id",
                        "as": "ChemistDetails",
                    }
                },
                {"$set": {"amount": {"$multiply": ["$quantity", "$unit_price"]}}},
                {
                    "$group": {
                        "_id": group_id,
                        "total_amount": {"$sum": "$amount"},
                        "shop_name": {
                            "$first": {
                                "$arrayElemAt": ["$ChemistDetails.shop_name", 0]
                            }
                        },
                        "chemist_name_first_name": {
                            "$first": {
                                "$arrayElemAt": ["$ChemistDetails.name.first_name", 0]
                            }
                        },
                        "chemist_name_last_name": {
                            "$first": {
                                "$arrayElemAt": ["$ChemistDetails.name.last_name", 0]
                            }
                        },
                    }
                },
            ]
        )

        results = await self.collection.aggregate(pipeline).to_list(length=None)
        return results


    async def get_total_sales_category(
        self, chemist_id: str, movement: str, month: int, year: int
    ):
        import calendar
        from datetime import datetime

        start_date = datetime(year=year, month=month, day=1)
        last_day = calendar.monthrange(year, month)[1]
        end_date = datetime(year=year, month=month, day=last_day)
        pipeline = (
            [
                {
                    "$match": {
                        "chemist_id": chemist_id,
                        "movement_type": movement,
                        "created_at": {"$gte": start_date, "$lte": end_date},
                    }
                },
            ]
            if chemist_id != ""
            else []
        )
        pipeline.extend(
            [
                {"$set": {"amount": {"$multiply": ["$quantity", "$unit_price"]}}},
                {
                    "$lookup": {
                        "from": "Product",
                        "localField": "product_id",
                        "foreignField": "_id",
                        "as": "productDetails",
                        "pipeline": [{"$project": {"category": 1}}],
                    }
                },
                {"$set": {"productDetails": {"$arrayElemAt": ["$productDetails", 0]}}},
                {
                    "$group": {
                        "_id": "$productDetails.category",
                        "total_amount": {"$sum": "$amount"},
                    }
                },
                {
                    "$project": {
                        "label": "$_id",
                        "_id": 0,
                        "total_amount": 1
                    }
                }
            ]
        )
        results = await self.collection.aggregate(pipeline=pipeline).to_list(None)

        # Compute grand total
        grand_total = sum(item["total_amount"] for item in results)

        # Add percentage
        for item in results:
            item["value"] = (
                round((item["total_amount"] / grand_total) * 100, 2)
                if grand_total > 0
                else 0.0
            )

        return results
    
    async def get_top_category_monthly_user(
        self, chemist_id: str, movement: str, month: int, year: int
    ):
        import calendar

        # Calculate start and end dates for the year
        start_date = datetime(year=year, month=1, day=1)
        end_date = datetime(year=year, month=12, day=31, hour=23, minute=59, second=59)

        # Pipeline to get total sales per category for the year
        match_stage = {
            "chemist_id": chemist_id,
            "movement_type": movement,
            "created_at": {"$gte": start_date, "$lte": end_date},
        }
        pipeline_top_categories = [
            {"$match": match_stage},
            {"$set": {"amount": {"$multiply": ["$quantity", "$unit_price"]}}},
            {
                "$lookup": {
                    "from": "Product",
                    "localField": "product_id",
                    "foreignField": "_id",
                    "as": "productDetails",
                    "pipeline": [{"$project": {"category": 1}}],
                }
            },
            {"$set": {"category": {"$arrayElemAt": ["$productDetails.category", 0]}}},
            {
                "$group": {
                    "_id": "$category",
                    "total_amount": {"$sum": "$amount"},
                }
            },
            {"$sort": {"total_amount": -1}},
            {"$limit": 5},
        ]
        top_categories_result = await self.collection.aggregate(pipeline_top_categories).to_list(None)
        top_categories = [entry["_id"] for entry in top_categories_result if entry["_id"] is not None]

        # Compute total sales across all categories for the year
        pipeline_total_sales = [
            {"$match": match_stage},
            {"$set": {"amount": {"$multiply": ["$quantity", "$unit_price"]}}},
            {
                "$group": {
                    "_id": None,
                    "total_sales": {"$sum": "$amount"},
                }
            }
        ]
        total_sales_result = await self.collection.aggregate(pipeline_total_sales).to_list(None)
        total_sales = total_sales_result[0]["total_sales"] if total_sales_result else 0

        # Prepare monthly sales for each top category
        data = []
        for category in top_categories:
            # Pipeline to get monthly sales for this category
            pipeline_monthly = [
                {"$match": match_stage},
                {"$set": {"amount": {"$multiply": ["$quantity", "$unit_price"]}}},
                {
                    "$lookup": {
                        "from": "Product",
                        "localField": "product_id",
                        "foreignField": "_id",
                        "as": "productDetails",
                        "pipeline": [{"$project": {"category": 1, "product_name": 1}}],
                    }
                },
                {"$set": {"productDetails": {"$arrayElemAt": ["$productDetails", 0]}}},
                {"$match": {"productDetails.category": category}},
                {
                    "$group": {
                        "_id": {
                            "month": {"$month": "$created_at"},
                        },
                        "total_amount": {"$sum": "$amount"},
                    }
                },
            ]
            monthly_result = await self.collection.aggregate(pipeline_monthly).to_list(None)
            # Map month to total_amount
            month_to_amount = {entry["_id"]["month"]: entry["total_amount"] for entry in monthly_result}
            # Fill all months with 0 if missing
            monthly_data = [month_to_amount.get(m, 0) for m in range(1, 13)]

            data.append({
                "id": category,
                "label": category.capitalize() if isinstance(category, str) else str(category),
                "data": monthly_data,
            })

        return {
            "year": year,
            "total_sales": total_sales,
            "data": data,
        }

    async def get_top_category_yearly_admin(
        self, chemist_id: str, movement: str, month: int, year: int
    ):
        import calendar

        # Calculate start and end dates for the year
        start_date = datetime(year=year, month=1, day=1)
        end_date = datetime(year=year, month=12, day=31, hour=23, minute=59, second=59)

        # For admin, chemist_id is ignored (all chemists)
        match_stage = {
            "movement_type": movement,
            "created_at": {"$gte": start_date, "$lte": end_date},
        }
        pipeline_top_categories = [
            {"$match": match_stage},
            {"$set": {"amount": {"$multiply": ["$quantity", "$unit_price"]}}},
            {
                "$lookup": {
                    "from": "Product",
                    "localField": "product_id",
                    "foreignField": "_id",
                    "as": "productDetails",
                    "pipeline": [{"$project": {"category": 1}}],
                }
            },
            {"$set": {"category": {"$arrayElemAt": ["$productDetails.category", 0]}}},
            {
                "$group": {
                    "_id": "$category",
                    "total_amount": {"$sum": "$amount"},
                }
            },
            {"$sort": {"total_amount": -1}},
            {"$limit": 5},
        ]
        top_categories_result = await self.collection.aggregate(pipeline_top_categories).to_list(None)
        top_categories = [entry["_id"] for entry in top_categories_result if entry["_id"] is not None]

        # Compute total sales across all categories for the year
        pipeline_total_sales = [
            {"$match": match_stage},
            {"$set": {"amount": {"$multiply": ["$quantity", "$unit_price"]}}},
            {
                "$group": {
                    "_id": None,
                    "total_sales": {"$sum": "$amount"},
                }
            }
        ]
        total_sales_result = await self.collection.aggregate(pipeline_total_sales).to_list(None)
        total_sales = total_sales_result[0]["total_sales"] if total_sales_result else 0

        # Prepare monthly sales for each top category
        data = []
        for category in top_categories:
            pipeline_monthly = [
                {"$match": match_stage},
                {"$set": {"amount": {"$multiply": ["$quantity", "$unit_price"]}}},
                {
                    "$lookup": {
                        "from": "Product",
                        "localField": "product_id",
                        "foreignField": "_id",
                        "as": "productDetails",
                        "pipeline": [{"$project": {"category": 1, "product_name": 1}}],
                    }
                },
                {"$set": {"productDetails": {"$arrayElemAt": ["$productDetails", 0]}}},
                {"$match": {"productDetails.category": category}},
                {
                    "$group": {
                        "_id": {
                            "month": {"$month": "$created_at"},
                        },
                        "total_amount": {"$sum": "$amount"},
                    }
                },
            ]
            monthly_result = await self.collection.aggregate(pipeline_monthly).to_list(None)
            month_to_amount = {entry["_id"]["month"]: entry["total_amount"] for entry in monthly_result}
            monthly_data = [month_to_amount.get(m, 0) for m in range(1, 13)]

            data.append({
                "id": category,
                "label": category.capitalize() if isinstance(category, str) else str(category),
                "data": monthly_data,
            })

        return {
            "year": year,
            "total_sales": total_sales,
            "data": data,
        }

    async def get_sales_trends(
        self, chemist_id: str, movement: str, month: Union[int, None], year: int
    ):
        import calendar

        if month is not None:
            # Day-wise for the given month
            start_date = datetime(year=int(year), month=int(month), day=1)
            last_day = calendar.monthrange(int(year), int(month))[1]
            end_date = datetime(year=int(year), month=int(month), day=last_day, hour=23, minute=59, second=59)
            pipeline = (
                [
                    {
                        "$match": {
                            "chemist_id": chemist_id,
                            "movement_type": movement,
                            "created_at": {"$gte": start_date, "$lte": end_date},
                        }
                    },
                ]
                if chemist_id != ""
                else []
            )
            pipeline.extend(
                [
                    {"$set": {"amount": {"$multiply": ["$quantity", "$unit_price"]}}},
                    {
                        "$group": {
                            "_id": {
                                "$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}
                            },
                            "total_amount": {"$sum": "$amount"},
                        }
                    },
                ]
            )
            result = await self.collection.aggregate(pipeline=pipeline).to_list(None)
            result_dict = {entry["_id"]: entry["total_amount"] for entry in result}
            full_month_data = []
            labels = []
            for day in range(1, last_day + 1):
                date_obj = datetime(int(year), int(month), day)
                date_str = date_obj.strftime("%Y-%m-%d")
                if date_str in result_dict:
                    labels.append(date_str)
                    full_month_data.append(result_dict[date_str])
            return {"month": month, "year": year, "labels": labels, "data": full_month_data}
        else:
            # Month-wise for the given year
            start_date = datetime(year=int(year), month=1, day=1)
            end_date = datetime(year=int(year), month=12, day=31, hour=23, minute=59, second=59)
            pipeline = (
                [
                    {
                        "$match": {
                            "chemist_id": chemist_id,
                            "movement_type": movement,
                            "created_at": {"$gte": start_date, "$lte": end_date},
                        }
                    },
                ]
                if chemist_id != ""
                else []
            )
            pipeline.extend(
                [
                    {"$set": {"amount": {"$multiply": ["$quantity", "$unit_price"]}}},
                    {
                        "$group": {
                            "_id": {
                                "$dateToString": {"format": "%Y-%m", "date": "$created_at"}
                            },
                            "total_amount": {"$sum": "$amount"},
                        }
                    },
                ]
            )
            result = await self.collection.aggregate(pipeline=pipeline).to_list(None)
            result_dict = {entry["_id"]: entry["total_amount"] for entry in result}
            labels = []
            full_year_data = []
            for m in range(1, 13):
                date_str = f"{year}-{m:02d}"
                if date_str in result_dict:
                    labels.append(date_str)
                    full_year_data.append(result_dict[date_str])
            return {"month": None, "year": year, "labels": labels, "data": full_year_data}

    async def get_sales_trends_mont_wise(
        self, chemist_id: str, movement: str, month: int = None, year: int = None
    ):
        from datetime import datetime

        # Set full-year start and end
        start_date = datetime(year=year, month=1, day=1)
        end_date = datetime(year=year, month=12, day=31, hour=23, minute=59, second=59)

        # Base match condition
        match_condition = {
            "movement_type": movement,
            "created_at": {"$gte": start_date, "$lte": end_date},
        }
        if chemist_id:
            match_condition["chemist_id"] = chemist_id

        pipeline = [
            {"$match": match_condition},
            {"$set": {"amount": {"$multiply": ["$quantity", "$unit_price"]}}},
            {
                "$group": {
                    "_id": {
                        "month": {
                            "$dateToString": {"format": "%Y-%m", "date": "$created_at"}
                        }
                    },
                    "amount": {"$sum": "$amount"},
                }
            },
        ]

        result = await self.collection.aggregate(pipeline=pipeline).to_list(None)

        # Convert result to dict like {'2025-01': 1000, '2025-02': 0, ...}
        result_dict = {entry["_id"]["month"]: entry["amount"] for entry in result}

        # Fill 12 months
        full_year_data = []
        for m in range(1, 13):
            date_str = f"{year}-{m:02d}"
            full_year_data.append(result_dict.get(date_str, 0))

        return {"year": year, "data": full_year_data}


stock_movement_repo = StockMovementRepo()
