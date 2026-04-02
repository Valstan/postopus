import importlib.util
from pathlib import Path

module_path = Path("d:/PROGRAMMING/postopus/bin/rw/get_attach.py")
spec = importlib.util.spec_from_file_location("get_attach_mod", str(module_path))
get_attach_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(get_attach_mod)
get_attach = get_attach_mod.get_attach

sample = {
    "owner_id": -42320333,
    "text": "Test post with video",
    "attachments": [{"type": "video", "video": {"owner_id": -42320333, "id": 340363}}],
}

attach_str, count = get_attach(sample)
print("attach_str:", attach_str)
print("count:", count)
