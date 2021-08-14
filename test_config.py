import os

from bin.rw.open_file_json import open_file_json
from bin.rw.save_file_json import save_file_json

i = open_file_json('', "config")
os.rename('config.json', 'old_config.json')
save_file_json("", "config", i)

'''new = []
for i in delete_msg_blacklist:
    ii = i.lower()
    if ii not in new:
        new.append(ii)
write_json('new_config', new)
'''