from pymongo import MongoClient


def get_mongo_base():
    client = MongoClient(
        "mongodb+srv://valstan:nitro2000@postopus.qjxr9.mongodb.net/postopus?retryWrites=true&w=majority")
    db = client["postopus"]
    return db
