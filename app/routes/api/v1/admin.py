from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi import APIRouter

admin = APIRouter()

@admin.get('/routes1',response_class=ORJSONResponse)
async def route():
    return {'routes': ['route1','route2','route3']}

