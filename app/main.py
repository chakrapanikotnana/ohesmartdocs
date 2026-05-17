import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from starlette.middleware.sessions import SessionMiddleware

from app.routes.auth_routes import router as auth_router
from app.routes.upload_routes import router as upload_router
from app.routes.data_routes import router as data_router

app = FastAPI()

# Session middleware
app.add_middleware(
    SessionMiddleware,
    secret_key="demo-secret-key"
)

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

# Static files
app.mount(
    "/static",
    StaticFiles(directory=os.path.join(BASE_DIR, "static")),
    name="static"
)

# Register routes
app.include_router(auth_router)
app.include_router(upload_router)
app.include_router(data_router)