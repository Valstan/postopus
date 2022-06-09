import os

from pymongo import MongoClient


def get_mongo_base():
    client = MongoClient(os.getenv('MONGO_CLIENT'))
    db = client["postopus"]
    return db
