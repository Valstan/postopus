from pymongo import MongoClient


def get_mongo_base(session):
    client = MongoClient(session['MONGO_CLIENT'])
    db = client["postopus"]
    return db
