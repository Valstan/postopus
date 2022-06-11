from bin.rw.get_mongo_base import get_mongo_base
from logpass import VK_LOGIN_VALSTAN, VK_PASSWORD_VALSTAN, VK_LOGIN_BRIGADIR, VK_PASSWORD_BRIGADIR, VK_LOGIN_DRAN, \
    VK_PASSWORD_DRAN, INSTA_LOGIN_MI, INSTA_PASSWORD_MI, TIKTOK_LOGIN_MI, TIKTOK_PASSWORD_MI, TELEGA_TOKEN_VALSTANBOT, \
    MONGO_CLIENT


def get_session(name_base, name_collection, name_session):

    session = {"MONGO_CLIENT": MONGO_CLIENT}
    collection = get_mongo_base(session)[name_collection]
    session = collection.find_one({'title': name_collection})
    session.update(session['config_bases'][name_base])
    del session['config_bases']
    session.update({"name_session": name_session})
    session.update({"VK_LOGIN_VALSTAN": VK_LOGIN_VALSTAN})
    session.update({"VK_PASSWORD_VALSTAN": VK_PASSWORD_VALSTAN})
    session.update({"VK_LOGIN_BRIGADIR": VK_LOGIN_BRIGADIR})
    session.update({"VK_PASSWORD_BRIGADIR": VK_PASSWORD_BRIGADIR})
    session.update({"VK_LOGIN_VALSTAN": VK_LOGIN_VALSTAN})
    session.update({"VK_LOGIN_DRAN": VK_LOGIN_DRAN})
    session.update({"VK_PASSWORD_DRAN": VK_PASSWORD_DRAN})
    session.update({"INSTA_LOGIN_MI": INSTA_LOGIN_MI})
    session.update({"INSTA_PASSWORD_MI": INSTA_PASSWORD_MI})
    session.update({"TIKTOK_LOGIN_MI": TIKTOK_LOGIN_MI})
    session.update({"TIKTOK_PASSWORD_MI": TIKTOK_PASSWORD_MI})
    session.update({"TELEGA_TOKEN_VALSTANBOT": TELEGA_TOKEN_VALSTANBOT})
    session.update({"MONGO_CLIENT": MONGO_CLIENT})

    return session
