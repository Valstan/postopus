from bin.utils.search_text import search_text
from env_loader import logger, session


def load_table(name_table):
    """Load a table document from the current session['name_base'] collection.

    NOTE: callers may temporarily switch session['name_base'] when they need
    to load from a regional collection.
    """
    # Defensive: if Mongo is not available, return a default empty table
    if session.get("MONGO_BASE") is None:
        logger.error(
            f"MongoDB not available, cannot load table '{name_table}' - returning empty default table"
        )
        if name_table in ("config", "billboard"):
            return {}
        return {"lip": [], "hash": [], "title": name_table}
    collection = session["MONGO_BASE"][session["name_base"]]
    # use explicit membership checks instead of substring-in-string
    if name_table in ("novost", "novosti"):
        table = collection.find_one({"title": "novost"}, {"_id": 0, "title": 0})
    elif name_table == "config" and session.get("name_base") == "config":
        # 'delete_msg_blacklist' подгружается с локального диска
        table = collection.find_one(
            {"title": "config"}, {"delete_msg_blacklist": 0, "_id": 0, "title": 0}
        )
    else:
        table = collection.find_one({"title": name_table}, {"_id": 0, "title": 0})

    # Ensure expected list fields exist for writable tables
    if name_table not in ("config", "billboard"):
        if table:
            for key in ("lip", "hash"):
                if not table.get(key):
                    table[key] = []
        else:
            table = {"lip": [], "hash": [], "title": name_table}

    return table


def save_table(name_table):
    if "table_size" in session["work"][name_table]:
        size = session["work"][name_table]["table_size"]
    else:
        size = 30
    if session.get("MONGO_BASE") is None:
        logger.error(f"MongoDB not available, skipping save_table('{name_table}')")
        return
    collection = session["MONGO_BASE"][session["name_base"]]
    # Изменяем размеры таблиц содержащих только списки
    for n in session["work"][name_table].keys():
        if search_text(["lip", "hash"], n):
            while len(session["work"][name_table][n]) > size:
                del session["work"][name_table][n][0]
    collection.update_one({"title": name_table}, {"$set": session["work"][name_table]}, upsert=True)


if __name__ == "__main__":
    pass
