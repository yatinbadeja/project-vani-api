from fastapi import HTTPException
from app.database.repositories.Sales import sales_repo
from typing import List, Dict
from fastapi import APIRouter

Analytics = APIRouter()

@Analytics.get("/total_sales_amount")
async def get_total_sales_amount() -> Dict:
    """
    API endpoint for Chart 1: Total sales amount (for all chemists combined).
    """
    try:
        # Calculate the total sales amount for all chemists
        result = await sales_repo.collection.aggregate(
            [
                {
                    "$group": {
                        "_id": None,  # Group all documents into a single group
                        "total_sales_amount": {"$sum": "$amount"},
                    }
                }
            ]
        ).to_list(
            length=None
        )  # Convert the aggregation result to a list

        if result:
            total_sales_amount = result[0].get("total_sales_amount", 0)
        else:
            total_sales_amount = 0

        return {"success": True, "data": {"total_sales_amount": total_sales_amount}}
    except Exception as e:
        print(f"Error in get_total_sales_amount: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@Analytics.get("/sales_per_chemist_amount")
async def get_sales_per_chemist_amount() -> Dict:
    """
    API endpoint for Chart 2: Total sales amount per chemist.
    """
    try:
        # Aggregate sales data to get total sales amount per chemist
        sales_data = await sales_repo.collection.aggregate(
            [
                {
                    "$group": {
                        "_id": "$chemist_id",
                        "total_sales_amount": {"$sum": "$amount"},
                    }
                },
                {
                    "$lookup": {
                        "from": "Chemist",  # Join with the Chemist collection to get chemist details
                        "localField": "_id",
                        "foreignField": "chemist_id",
                        "as": "chemist_data",
                    }
                },
                {"$unwind": "$chemist_data"},  # Flatten the chemist_data array
                {
                    "$project": {
                        "_id": 0,
                        "chemist_id": "$_id",
                        "chemist_name": "$chemist_data.name",  # Assuming 'name' field in Chemist collection
                        "total_sales_amount": 1,
                    }
                },
            ]
        ).to_list(length=None)

        return {"success": True, "data": sales_data}
    except Exception as e:
        print(f"Error in get_sales_per_chemist_amount: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")



# Top 5 pharmacy by sales
@Analytics.get("/top_5_pharmacies_by_sales")
async def get_top_5_pharmacies_by_sales() -> Dict:
    """
    API endpoint to get the top 5 pharmacies by sales.
    """
    try:
        # Aggregate sales data to get total sales per chemist, sorted and limited to top 5
        top_5_sales = await sales_repo.collection.aggregate(
            [
                {
                    "$group": {
                        "_id": "$chemist_id",
                        "total_sales": {"$sum": "$total_amount"},
                    }
                },
                {"$sort": {"total_sales": -1}},  # Sort in descending order of total_sales
                {"$limit": 5},  # Limit the result to the top 5
                {
                    "$lookup": {
                        "from": "Chemist",  # Join with the Chemist collection to get chemist details
                        "localField": "_id",
                        "foreignField": "chemist_id",
                        "as": "chemist",
                    }
                },
                {"$unwind": "$chemist"},  # Flatten the chemist array
                {
                    "$project": {
                        "_id": 0,
                        "chemist_id": "$_id",
                        "chemist_name": "$chemist.name",  # Get the chemist name
                        "total_sales": 1,
                    }
                },
            ]
        ).to_list(length=None)

        return {"success": True, "data": top_5_sales}
    except Exception as e:
        print(f"Error in get_top_5_pharmacies_by_sales: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
