from config import delete_msg_blacklist
from moduls.read_write.write_json import writejson

new = []
for i in delete_msg_blacklist:
    ii = i.lower()
    if ii not in new:
        new.append(ii)
writejson('new_config', new)
