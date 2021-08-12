from bin.rw.get_json import get_json
from bin.rw.write_json import write_json

i = get_json({'path_bases': "", 'base': "", 'category': "config"})
write_json({'path_bases': "", 'base': "", 'category': "config"}, i)

'''new = []
for i in delete_msg_blacklist:
    ii = i.lower()
    if ii not in new:
        new.append(ii)
write_json('new_config', new)
'''