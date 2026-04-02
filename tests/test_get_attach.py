from bin.rw.get_attach import get_attach


def test_get_attach_video():
    sample = {"attachments": [{"type": "video", "video": {"owner_id": -42320333, "id": 340363}}]}
    attach_str, count = get_attach(sample)
    assert attach_str == "video-42320333_340363"
    assert count == 1


def test_get_attach_photos_list():
    sample = {
        "attachments": [
            {
                "type": "photos_list",
                "photos_list": [{"owner_id": 100, "id": 1}, {"owner_id": 100, "id": 2}],
            }
        ]
    }
    attach_str, count = get_attach(sample)
    items = attach_str.split(",") if attach_str else []
    assert "photo100_1" in items and "photo100_2" in items
    assert count == 2


def test_get_attach_audio_video_conflict():
    sample = {
        "attachments": [
            {"type": "audio", "audio": {"owner_id": 1, "id": 10}},
            {"type": "video", "video": {"owner_id": -2, "id": 20}},
        ]
    }
    attach_str, count = get_attach(sample)
    # video should be present, audio should be removed in conflict
    assert "video-2_20" in attach_str
    assert "audio" not in attach_str
    assert count == 1
