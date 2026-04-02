from env_loader import session


def sort_old_date(sample):

    difference = session["timestamp_now"] - sample["date"]

    # Используем кортежи для корректной проверки принадлежности темы к списку
    if session["name_session"] in ("admin", "novost", "reklama", "sosed", "malmig") and difference < session["time_old_post"]["hard"]:
        return True
    elif session["name_session"] in ("detsad", "kultura", "union", "sport", "oblast_novost") and difference < session["time_old_post"]["medium"]:
        return True
    elif session["name_session"] in ("krugozor", "music", "kino", "prikol", "art", "repost_kultpodved") and difference < session["time_old_post"]["light"]:
        return True
    else:
        return False
