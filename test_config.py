from bin.rw import RWFile

i = RWFile('', "config")
i.open()
i.rename()
i.save()

'''new = []
for i in delete_msg_blacklist:
    ii = i.lower()
    if ii not in new:
        new.append(ii)
write_json('new_config', new)
'''