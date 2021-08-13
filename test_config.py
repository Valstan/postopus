import os

from bin.rw.get_json import get_json
from bin.rw.write_json import write_json

i = get_json('', "config")
os.rename('config.json', 'old_config.json')
write_json("", "config", i)

'''new = []
for i in delete_msg_blacklist:
    ii = i.lower()
    if ii not in new:
        new.append(ii)
write_json('new_config', new)
'''