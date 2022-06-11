import os

from bin.rw.get_mongo_base import get_mongo_base


def get_session(name_base, name_collection, name_session):

    session = {"MONGO_CLIENT": os.getenv("MONGO_CLIENT")}
    collection = get_mongo_base(session)[name_collection]
    session = collection.find_one({'title': name_collection})
    session.update(session['config_bases'][name_base])
    del session['config_bases']
    session.update({"name_session": name_session})
    session.update({"VK_LOGIN_VALSTAN": os.getenv("VK_LOGIN_VALSTAN")})
    session.update({"VK_PASSWORD_VALSTAN": os.getenv("VK_PASSWORD_VALSTAN")})
    session.update({"VK_LOGIN_BRIGADIR": os.getenv("VK_LOGIN_BRIGADIR")})
    session.update({"VK_PASSWORD_BRIGADIR": os.getenv("VK_PASSWORD_BRIGADIR")})
    session.update({"VK_LOGIN_VALSTAN": os.getenv("VK_LOGIN_VALSTAN")})
    session.update({"VK_LOGIN_DRAN": os.getenv("VK_LOGIN_DRAN")})
    session.update({"VK_PASSWORD_DRAN": os.getenv("VK_PASSWORD_DRAN")})
    session.update({"INSTA_LOGIN_MI": os.getenv("INSTA_LOGIN_MI")})
    session.update({"INSTA_PASSWORD_MI": os.getenv("INSTA_PASSWORD_MI")})
    session.update({"TIKTOK_LOGIN_MI": os.getenv("TIKTOK_LOGIN_MI")})
    session.update({"TIKTOK_PASSWORD_MI": os.getenv("TIKTOK_PASSWORD_MI")})
    session.update({"TELEGA_TOKEN_VALSTANBOT": os.getenv("TELEGA_TOKEN_VALSTANBOT")})
    session.update({"MONGO_CLIENT": os.getenv("MONGO_CLIENT")})

    return session
