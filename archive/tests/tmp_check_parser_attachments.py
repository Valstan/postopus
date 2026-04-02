# Quick check to simulate parser behavior for attachments
sample = {
    "owner_id": -42320333,
    "text": "Test post with video",
    "attachments": [{"type": "video", "video": {"owner_id": -42320333, "id": 340363}}],
}

# Simulate the parser logic change
theme = "novost"

if theme == "reklama" and "attachments" in sample:
    del sample["attachments"]

print("attachments_present:", "attachments" in sample)
print("attachments_value:", sample.get("attachments"))
