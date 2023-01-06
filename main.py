from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.routers import router
from config.config import config
from database.database import init_db

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    config()
    init_db()


app.include_router(router, prefix="/api")
