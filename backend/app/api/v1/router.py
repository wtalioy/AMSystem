from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, cars, orders, workers, admin

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/login", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(cars.router, prefix="/cars", tags=["cars"])
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])
api_router.include_router(workers.router, prefix="/workers", tags=["workers"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
