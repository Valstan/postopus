"""
Legacy VK: извлечение вложений из поста.

Портировано из old_postopus/bin/rw/get_attach.py.
Адаптировано: убрана зависимость от session, чистые функции.
"""


def get_attach(msg: dict, max_count: int = 10) -> tuple[str, int]:
    """
    Извлекает вложения из поста VK.

    Returns:
        (attachments_str, count) — строка для wall.post(attachments=...)
    """
    if "attachments" not in msg or not msg["attachments"]:
        return "", 0

    items: list[str] = []
    count = 0
    has_audio = False
    has_video = False

    for at in msg["attachments"]:
        if count >= max_count:
            break

        t = at.get("type")
        if not t or t == "link":
            continue

        def fmt(prefix: str, owner, _id) -> str:
            return f"{prefix}{owner}_{_id}"

        if t == "photo":
            inner = at.get("photo") or {}
            owner = inner.get("owner_id") or inner.get("user_id") or inner.get("from_id")
            _id = inner.get("id")
            if owner is not None and _id is not None:
                items.append(fmt("photo", owner, _id))
                count += 1

        elif t in ("photos_list", "photo_list", "album"):
            photos = at.get(t) or at.get("photos_list") or at.get("album") or at.get("photo")
            if isinstance(photos, list):
                for p in photos:
                    if count >= max_count:
                        break
                    owner = p.get("owner_id") or p.get("user_id") or p.get("from_id")
                    _id = p.get("id")
                    if owner is not None and _id is not None:
                        items.append(fmt("photo", owner, _id))
                        count += 1
            elif isinstance(photos, dict):
                owner = photos.get("owner_id") or photos.get("user_id") or photos.get("from_id")
                _id = photos.get("id")
                if owner is not None and _id is not None and count < max_count:
                    items.append(fmt("photo", owner, _id))
                    count += 1

        elif t == "video":
            inner = at.get("video") or {}
            owner = inner.get("owner_id") or inner.get("owner")
            _id = inner.get("id")
            if owner is not None and _id is not None:
                has_video = True
                items.append(fmt("video", owner, _id))
                count += 1

        elif t == "audio":
            inner = at.get("audio") or {}
            owner = inner.get("owner_id") or inner.get("owner")
            _id = inner.get("id")
            if owner is not None and _id is not None:
                has_audio = True
                items.append(fmt("audio", owner, _id))
                count += 1

        elif t == "doc":
            inner = at.get("doc") or {}
            owner = inner.get("owner_id") or inner.get("user_id") or inner.get("from_id")
            _id = inner.get("id")
            if owner is not None and _id is not None:
                items.append(fmt("doc", owner, _id))
                count += 1

        else:
            inner = at.get(t) or {}
            if isinstance(inner, dict):
                owner = inner.get("owner_id") or inner.get("user_id") or inner.get("from_id")
                _id = inner.get("id")
                if owner is not None and _id is not None:
                    items.append(fmt(t, owner, _id))
                    count += 1

    # Если есть и аудио и видео — оставляем только видео
    if has_audio and has_video:
        items = [i for i in items if not i.startswith("audio")]
        count = len(items)

    return ",".join(items), count
