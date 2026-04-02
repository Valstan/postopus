def get_attach(msg, max_count=10):
    """Extract attachments from a VK message dict.

    Returns a tuple `(attachments_str, count)` where `attachments_str` is a
    comma-separated string suitable for passing to VK `wall.post(..., attachments=...)`.

    Supported types: photo(s), video, audio, doc and generic attachments when identifiable.
    By default `link` attachments are skipped to preserve existing behaviour.

    The function prefers video over audio when both are present.
    """
    if "attachments" not in msg or not msg["attachments"]:
        return "", 0

    items = []
    count = 0
    has_audio = False
    has_video = False

    for at in msg["attachments"]:
        if count >= max_count:
            break

        t = at.get("type")
        if not t:
            continue

        # Skip link attachments (preserve previous behaviour)
        if t == "link":
            continue

        # Helper to format owner/id pairs
        def fmt(prefix, owner, _id):
            return f"{prefix}{owner}_{_id}"

        # PHOTO (single)
        if t == "photo":
            inner = at.get("photo") or {}
            owner = inner.get("owner_id") or inner.get("user_id") or inner.get("from_id")
            _id = inner.get("id")
            if owner is not None and _id is not None:
                items.append(fmt("photo", owner, _id))
                count += 1

        # photos_list / album / multiple photos
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

        # VIDEO
        elif t == "video":
            inner = at.get("video") or {}
            owner = inner.get("owner_id") or inner.get("owner")
            _id = inner.get("id")
            if owner is not None and _id is not None:
                has_video = True
                items.append(fmt("video", owner, _id))
                count += 1

        # AUDIO
        elif t == "audio":
            inner = at.get("audio") or {}
            owner = inner.get("owner_id") or inner.get("owner")
            _id = inner.get("id")
            if owner is not None and _id is not None:
                has_audio = True
                items.append(fmt("audio", owner, _id))
                count += 1

        # DOC
        elif t == "doc":
            inner = at.get("doc") or {}
            owner = inner.get("owner_id") or inner.get("user_id") or inner.get("from_id")
            _id = inner.get("id")
            if owner is not None and _id is not None:
                items.append(fmt("doc", owner, _id))
                count += 1

        # Generic fallback for other attachment types that include owner/id
        else:
            inner = at.get(t) or {}
            if isinstance(inner, dict):
                owner = inner.get("owner_id") or inner.get("user_id") or inner.get("from_id")
                _id = inner.get("id")
                if owner is not None and _id is not None:
                    items.append(fmt(t, owner, _id))
                    count += 1

    # If both audio and video present, keep only video attachments
    if has_audio and has_video:
        items = [i for i in items if not i.startswith("audio")]
        count = len(items)

    return ",".join(items), count


if __name__ == "__main__":
    pass
