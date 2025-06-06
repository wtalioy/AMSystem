from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth, 
    users, 
    cars, 
    orders, 
    logs, 
    wage, 
    procedures, 
    statistics,
    payments,
    workers,
    audit
)

api_router = APIRouter()

# Core services
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(cars.router, prefix="/cars", tags=["Cars"])

# Order and Procedure management
api_router.include_router(orders.router, prefix="/orders", tags=["Orders"])
api_router.include_router(procedures.router, prefix="/procedures", tags=["Procedures"])

# Worker and Admin specific functionalities
api_router.include_router(workers.router, prefix="/workers", tags=["Worker Management"])
api_router.include_router(logs.router, prefix="/logs", tags=["Maintenance Logs"])
api_router.include_router(wage.router, prefix="/wage", tags=["Wage & Income"])
api_router.include_router(statistics.router, prefix="/statistics", tags=["Statistics"])
api_router.include_router(payments.router, prefix="/payments", tags=["Payments"])
api_router.include_router(audit.router, prefix="/audit", tags=["Audit & Rollback"])
