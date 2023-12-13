from fastapi import FastAPI
from .notification_main import notification_router

# Create the main FastAPI application instance
app = FastAPI()

# Attach the routers to the main application
app.include_router(notification_router)