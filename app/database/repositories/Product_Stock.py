from app.Config import ENV_PROJECT
from .crud.base_mongo_crud import BaseMongoDbCrud
from app.database.models.Product_Stock import ProductStock, ProductStockDB
from typing import List
from pymongo import UpdateOne
from app.database.repositories.crud.base import (
    PageRequest,
    Meta,
    PaginatedResponse,
    SortingOrder,
    Sort,
    Page,
)


class ProductStockRepo(BaseMongoDbCrud):
    def __init__(self):
        super().__init__(ENV_PROJECT.MONGO_DATABASE, "ProductStock", unique_attributes=[])

    async def new(self, sub: ProductStock):
        return await self.save(ProductStockDB(**sub.model_dump()))

    async def get_product_stock(self, product_id: str, chemist_id: str):
        print("product_Id", product_id)
        return await self.collection.find_one(
            {"product_id": product_id, "chemist_id": chemist_id}
        )

    async def bulk_write(self, operations: List[UpdateOne]):
        if operations:
            return await self.collection.bulk_write(operations)

    async def insert_many(self, products: List[ProductStockDB]):
        if products:
            documents = [
                {**doc.model_dump(), "_id": str(doc.product_stock_id)} for doc in products
            ]
            return await self.collection.insert_many(documents)

    async def getProductStock(
        self,
        current_user_id: str,
        search: str,
        state: str,
        category: str,
        pagination: PageRequest,
        sort: Sort,
    ):
        filter_params = {
            "chemist_id": current_user_id,
        }


        # if search not in ["hello"]:
        #     filter_params["$or"] = [
        #         {
        #             "productDetails.product_name": {
        #                 "$regex": f"^{search}",
        #                 "$options": "i",
        #             }
        #         },
        #         {"productDetails.category": {"$regex": f"^{search}", "$options": "i"}},
        #     ]

        # if category not in ["hello"]:
        #     filter_params["category"] = category

        sort_fields_mapping = {
            "product_name": "productDetails.product_name",
            # "category": "productDetails.category",
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
            {"$match": filter_params},
            {
                "$lookup": {
                    "from": "Product",
                    "localField": "product_id",
                    "foreignField": "_id",
                    "as": "productDetails",
                    "pipeline": (
                        (
                                [{"$match": {"category": category}}] if category else []
                            ) +
                            (
                                [{
                                    "$match": {
                                        "$or": [
                                            {"product_name": {"$regex": search, "$options": "i"}},
                                            {"category": {"$regex": search, "$options": "i"}}
                                        ]
                                    }
                                }] if search else []
                            ) +
                        [
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
                    ]
                    ),
                }
            },
            {"$unwind": {"path": "$productDetails"}},
            # {
            #     "$lookup": {
            #         "from": "StockMovement",
            #         "localField": "product_id",
            #         "foreignField": "product_id",
            #         "as": "stock_movements",
            #         "pipeline": [
            #             {"$match": {"chemist_id": current_user_id}},
            #             {
            #                 "$project": {
            #                     "quantity": 1,
            #                     "unit_price": 1,
            #                     "movement_type": 1,
            #                 }
            #             },
            #         ],
            #     }
            # },
            # {
            #     "$addFields": {
            #         "purchase_price": {
            #             "$sum": {
            #                 "$map": {
            #                     "input": "$stock_movements",
            #                     "as": "movement",
            #                     "in": {
            #                         "$cond": {
            #                             "if": {"$eq": ["$$movement.movement_type", "IN"]},
            #                             "then": {
            #                                 "$multiply": [
            #                                     "$$movement.quantity",
            #                                     "$$movement.unit_price",
            #                                 ]
            #                             },
            #                             "else": {
            #                                 "$multiply": [
            #                                     "$$movement.quantity",
            #                                     {
            #                                         "$multiply": [
            #                                             "$$movement.unit_price",
            #                                             -1,
            #                                         ]
            #                                     },
            #                                 ]
            #                             },
            #                         }
            #                     },
            #                 }
            #             }
            #         }
            #     }
            # },
            {
                "$lookup": {
                    "from": "StockMovement",
                    "let": {"prod_id": "$product_id"},
                    "pipeline": [
                        {
                            "$match": {
                                "$expr": {
                                    "$and": [
                                        {"$eq": ["$product_id", "$$prod_id"]},
                                        {"$eq": ["$chemist_id", current_user_id]},
                                        {"$in": ["$movement_type", ["IN", "OUT"]]},
                                    ]
                                }
                            }
                        },
                        {
                            "$group": {
                                "_id": "$movement_type",
                                "total_quantity": {"$sum": "$quantity"},
                                "avg_price": {
                                    "$sum": {"$multiply": ["$unit_price", "$quantity"]}
                                },
                            }
                        },
                    ],
                    "as": "movementData",
                }
            },
            {
                "$addFields": {
                    "purchase_price": {
                        "$first": {
                            "$map": {
                                "input": {
                                    "$filter": {
                                        "input": "$movementData",
                                        "as": "m",
                                        "cond": {"$eq": ["$$m._id", "IN"]},
                                    }
                                },
                                "as": "x",
                                "in": "$$x.avg_price",
                            }
                        }
                    },
                    "sell_price": {
                        "$first": {
                            "$map": {
                                "input": {
                                    "$filter": {
                                        "input": "$movementData",
                                        "as": "m",
                                        "cond": {"$eq": ["$$m._id", "OUT"]},
                                    }
                                },
                                "as": "x",
                                "in": "$$x.avg_price",
                            }
                        }
                    },
                    "available_quantity": {
                        "$subtract": [
                            {
                                "$ifNull": [
                                    {
                                        "$first": {
                                            "$map": {
                                                "input": {
                                                    "$filter": {
                                                        "input": "$movementData",
                                                        "as": "m",
                                                        "cond": {
                                                            "$eq": ["$$m._id", "IN"]
                                                        },
                                                    }
                                                },
                                                "as": "x",
                                                "in": "$$x.total_quantity",
                                            }
                                        }
                                    },
                                    0,
                                ]
                            },
                            {
                                "$ifNull": [
                                    {
                                        "$first": {
                                            "$map": {
                                                "input": {
                                                    "$filter": {
                                                        "input": "$movementData",
                                                        "as": "m",
                                                        "cond": {
                                                            "$eq": ["$$m._id", "OUT"]
                                                        },
                                                    }
                                                },
                                                "as": "x",
                                                "in": "$$x.total_quantity",
                                            }
                                        }
                                    },
                                    0,
                                ]
                            },
                        ]
                    },
                }
            },
            {
                "$project": {
                    "product_id": 1,
                    "purchase_price": 1,
                    "sell_price": 1,
                    "available_quantity": 1,
                    "updated_at": 1,
                    "productDetails": {
                        "product_name": "$productDetails.product_name",
                        "category": "$productDetails.category",
                        "state": "$productDetails.state",
                        "measure_of_unit": "$productDetails.measure_of_unit",
                        "no_of_tablets_per_pack": "$productDetails.no_of_tablets_per_pack",
                        "storage_requirement": "$productDetails.storage_requirement",
                        "expiry_date": "$productDetails.expiry_date",
                        "description": "$productDetails.description",
                        "price": "$productDetails.price",
                    },
                }
            },
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
                    "unique_categories": [
                        {"$match": {"category": {"$ne": None}}},
                        {"$group": {"_id": "$category"}},
                        {"$project": {"_id": 0, "category": "$_id"}},
                        {"$sort": {"category": 1}},
                    ],
                }
            }
        )

        meta_pipeline = [
            {"$match": filter_params},
            {
                "$lookup": {
                    "from": "StockMovement",
                    "let": {"prod_id": "$product_id"},
                    "pipeline": [
                        {
                            "$match": {
                                "$expr": {
                                    "$and": [
                                        {"$eq": ["$product_id", "$$prod_id"]},
                                        {"$eq": ["$chemist_id", current_user_id]},
                                        {"$in": ["$movement_type", ["IN", "OUT"]]},
                                    ]
                                }
                            }
                        },
                        {
                            "$group": {
                                "_id": "$movement_type",
                                "total_quantity": {"$sum": "$quantity"},
                                "total_value": {
                                    "$sum": {"$multiply": ["$unit_price", "$quantity"]},
                                },
                            }
                        },
                    ],
                    "as": "movementData",
                }
            },
            {
                "$addFields": {
                    "in_quantity": {
                        "$ifNull": [
                            {
                                "$first": {
                                    "$map": {
                                        "input": {
                                            "$filter": {
                                                "input": "$movementData",
                                                "as": "m",
                                                "cond": {"$eq": ["$$m._id", "IN"]},
                                            }
                                        },
                                        "as": "x",
                                        "in": "$$x.total_quantity",
                                    }
                                }
                            },
                            0,
                        ]
                    },
                    "out_quantity": {
                        "$ifNull": [
                            {
                                "$first": {
                                    "$map": {
                                        "input": {
                                            "$filter": {
                                                "input": "$movementData",
                                                "as": "m",
                                                "cond": {"$eq": ["$$m._id", "OUT"]},
                                            }
                                        },
                                        "as": "x",
                                        "in": "$$x.total_quantity",
                                    }
                                }
                            },
                            0,
                        ]
                    },
                    "purchase_value": {
                        "$ifNull": [
                            {
                                "$first": {
                                    "$map": {
                                        "input": {
                                            "$filter": {
                                                "input": "$movementData",
                                                "as": "m",
                                                "cond": {"$eq": ["$$m._id", "IN"]},
                                            }
                                        },
                                        "as": "x",
                                        "in": "$$x.total_value",
                                    }
                                }
                            },
                            0,
                        ]
                    },
                    "sale_value": {
                        "$ifNull": [
                            {
                                "$first": {
                                    "$map": {
                                        "input": {
                                            "$filter": {
                                                "input": "$movementData",
                                                "as": "m",
                                                "cond": {"$eq": ["$$m._id", "OUT"]},
                                            }
                                        },
                                        "as": "x",
                                        "in": "$$x.total_value",
                                    }
                                }
                            },
                            0,
                        ]
                    },
                }
            },
            {
                "$addFields": {
                    "available_quantity": {"$subtract": ["$in_quantity", "$out_quantity"]}
                }
            },
            {
                "$group": {
                    "_id": None,
                    "purchase_value": {"$sum": "$purchase_value"},
                    "sale_value": {"$sum": "$sale_value"},
                    "positive_stock": {
                        "$sum": {"$cond": [{"$gt": ["$available_quantity", 5]}, 1, 0]}
                    },
                    "low_stock": {
                        "$sum": {"$cond": [{"$lt": ["$available_quantity", 5]}, 1, 0]}
                    },
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "purchase_value": 1,
                    "sale_value": 1,
                    "positive_stock": 1,
                    "low_stock": 1,
                }
            },
        ]

        result = [doc async for doc in self.collection.aggregate(pipeline)]
        res = result[0]

        docs = res["docs"]
        count = res["count"][0]["count"] if len(res["count"]) > 0 else 0
        unique_categories = [entry["category"] for entry in res["unique_categories"]]

        meta_result = [doc async for doc in self.collection.aggregate(meta_pipeline)]
        meta_stats = meta_result[0] if len(meta_result) > 0 else {}

        return PaginatedResponse(
            docs=docs,
            meta=Meta(
                **pagination.paging.model_dump(),
                total=count,
                unique=unique_categories,
                purchase_value=meta_stats.get("purchase_value", 0),
                sale_value=meta_stats.get("sale_value", 0),
                positive_stock=meta_stats.get("positive_stock", 0),
                low_stock=meta_stats.get("low_stock", 0),
            ),
        )

    async def product_stock_movement(self, chemist_id: str):
        pipeline = [{"$match": {"chemist_id": chemist_id}}] if chemist_id != "" else []
        pipeline.extend(
            [
                {
                    "$lookup": {
                        "from": "Product",
                        "localField": "product_id",
                        "foreignField": "_id",
                        "as": "Product",
                    }
                },
                {"$set": {"Product": {"$arrayElemAt": ["$Product", 0]}}},
                {
                    "$set": {
                        "amount": {"$multiply": ["$available_quantity", "$Product.price"]}
                    }
                },
                {"$group": {"_id": None, "_amount": {"$sum": "$amount"}}},
            ]
        )
        return await self.collection.aggregate(pipeline=pipeline).to_list(None)

    async def return_pending_stock_amount(self, chemist_id: str):
        import datetime

        time = datetime.datetime.now() - datetime.timedelta(days=180)
        group_id = None
        pipeline = [{"$match": {"chemist_id": chemist_id}}] if chemist_id != "" else []
        pipeline.extend(
            [
                {
                    "$lookup": {
                        "from": "Product",
                        "localField": "product_id",
                        "foreignField": "_id",
                        "as": "Product",
                    }
                },
                {"$set": {"Product": {"$arrayElemAt": ["$Product", 0]}}},
                {"$set": {"date": "$Product.expiry_date"}},
                {"$match": {"date": {"$gte": time, "$lte": datetime.datetime.now()}}},
                {
                    "$set": {
                        "amount": {"$multiply": ["$available_quantity", "$Product.price"]}
                    }
                },
                {
                    "$group": {
                        "_id": "$chemist_id" if chemist_id != "" else None,
                        "_amount": {"$sum": "$amount"},
                    }
                },
            ]
        )
        return await self.collection.aggregate(pipeline=pipeline).to_list(None)

    async def _return_pending_stock_amount(self, chemist_id: str):
        import datetime

        time = datetime.datetime.now() - datetime.timedelta(days=180)
        pipeline = [{"$match": {"chemist_id": chemist_id}}] if chemist_id != "" else []

        pipeline.extend(
            [
                {
                    "$lookup": {
                        "from": "Product",
                        "localField": "product_id",
                        "foreignField": "_id",
                        "as": "Product",
                    }
                },
                {"$set": {"Product": {"$arrayElemAt": ["$Product", 0]}}},
                {"$set": {"date": "$Product.expiry_date"}},
                {"$match": {"date": {"$lte": time}}},
                {
                    "$set": {
                        "amount": {"$multiply": ["$available_quantity", "$Product.price"]}
                    }
                },
                {"$group": {"_id": None, "_amount": {"$sum": "$amount"}}},
            ]
        )
        return await self.collection.aggregate(pipeline=pipeline).to_list(None)

    async def group_products_by_stock_level(self, chemist_id: str):
        pipeline = [{"$match": {"chemist_id": chemist_id}}] if chemist_id != "" else []
        pipeline.extend(
            [
                {
                    "$set": {
                        "stock_level": {
                            "$switch": {
                                "branches": [
                                    {
                                        "case": {"$lte": ["$available_quantity", 10]},
                                        "then": "Low",
                                    },
                                    {
                                        "case": {"$gte": ["$available_quantity", 200]},
                                        "then": "Overstock",
                                    },
                                ],
                                "default": "Normal",
                            }
                        }
                    }
                },
                {"$group": {"_id": "$stock_level", "count": {"$sum": 1}}},
            ]
        )
        results = await self.collection.aggregate(pipeline).to_list(None)

        # Ensure all stock levels are present
        stock_levels = {"Low": 0, "Normal": 0, "Overstock": 0}
        for entry in results:
            stock_levels[entry["_id"]] = entry["count"]

        return [
            {"stock_level": key, "count": value} for key, value in stock_levels.items()
        ]


product_stock_repo = ProductStockRepo()
