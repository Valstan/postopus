from config import bases, fbase
from moduls.read_write.get_json import getjson
from moduls.read_write.get_msg import get_msg
from moduls.read_write.get_session_vk_api import get_session_vk_api
from moduls.read_write.write_json import writejson
from moduls.utils.clear_copy_history import clear_copy_history


def aprel(prefix_base):
    base = getjson(bases + prefix_base + fbase)
    if 'shut_aprel' not in base:
        base['shut_aprel'] = []
    vkapp = get_session_vk_api(base['id']['l'], base['id']['p'])
    aprel_id = -144647350
    msgs = get_msg(vkapp, aprel_id, 0, 30)
    for msg in msgs:
        shut = clear_copy_history(shut)
        shut = ''.join(map(str, ('wall', shut['owner_id'], '_', shut['id'])))
        if shut not in base['shut_aprel']:
            break

    id_group = base['id']['post_group']['key'] * -1
    try:
        vkapp.wall.repost(object=shut, group_id=id_group)
        base['shut_reklama'].append(shut)
        while len(base['shut_reklama']) > 10:
            del base['shut_reklama'][0]
        writejson(bases + base['prefix'] + fbase, base)
        return True
    except:
        return False


if __name__ == '__main__':
    reklama('t')
