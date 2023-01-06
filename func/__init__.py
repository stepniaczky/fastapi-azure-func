import azure.functions as func
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.routers import router
from config.config import config
from database.database import init_db

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    config()
    init_db()


app.include_router(router, prefix="/api")


def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    return func.AsgiMiddleware(app).handle(req, context)
