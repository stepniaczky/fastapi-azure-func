import os

from pymongo import MongoClient
from fastapi import HTTPException
from pathlib import Path


def config():
    global CONFIG
    CONFIG = {
        'MONGODB_CONN_STRING': os.environ.get('MONGODB_CONN_STRING'),
        'DB': os.environ.get('DB')
    }

    if 'MONGODB_CONN_STRING' not in CONFIG or 'DB' not in CONFIG:
        raise HTTPException(
            status_code=500, detail='MongoDB connection string or database name not found in env file')


def get_client():
    try:
        return MongoClient(CONFIG['MONGODB_CONN_STRING'])
    except Exception:
        raise HTTPException(status_code=500, detail='MongoDB connection error')


def get_collection(collection_name):
    db = get_client()[CONFIG['DB']]
    if collection_name not in db.list_collection_names():
        db.command({'customAction': "CreateCollection",
                   'collection': collection_name})
        print("Created collection {}". format(collection_name))

    return db[collection_name]
