from bin.rw.get_attach import get_attach

sample = {
    "owner_id": -42320333,
    "text": "Test post with video",
    "attachments": [{"type": "video", "video": {"owner_id": -42320333, "id": 340363}}],
}

attach_str, count = get_attach(sample)
print("attach_str:", attach_str)
print("count:", count)
