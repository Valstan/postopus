from bin.rw.change_lp import change_lp
from config import bases, fbase, conf
from bin.rw.get_json import getjson
from bin.rw.get_msg import get_msg
from bin.rw.get_session_vk_api import get_session_vk_api
from bin.rw.write_json import writejson
from bin.utils.clear_copy_history import clear_copy_history


def aprel(prefix_base):
    base = getjson(bases + prefix_base + fbase)

    vkapp = get_session_vk_api(change_lp(prefix_base))
    aprel_id = -144647350
    msgs = get_msg(vkapp, aprel_id, 0, 10)
    msg_link = []

    for msg in msgs:
        msg = clear_copy_history(msg)
        msg_link = ''.join(map(str, ('wall', msg['owner_id'], '_', msg['id'])))
        if msg_link not in base['links']['aprel']:
            break

    if msg_link:
        id_group = -conf[base['prefix']]['post_group']['key']
        try:
            vkapp.wall.repost(object=msg_link, group_id=id_group)
            base['links']['aprel'].append(msg_link)
            while len(base['links']['aprel']) > 5:
                del base['links']['aprel'][0]
            writejson(bases + base['prefix'] + fbase, base)
            return True
        except:
            pass

    return False


if __name__ == '__main__':
    pass
