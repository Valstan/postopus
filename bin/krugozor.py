from bin.rw.change_lp import change_lp
from config import bases, fbase, conf
from bin.rw.get_json import getjson
from bin.rw.get_msg import get_msg
from bin.rw.get_session_vk_api import get_session_vk_api
from bin.rw.upload_post_to_main_group import upload_post_to_main_group
from bin.rw.write_json import writejson
from bin.utils.avtortut import avtortut
from bin.utils.clear_copy_history import clear_copy_history


def krugozor(prefix_base):
    base = getjson(bases + prefix_base + fbase)
    vkapp = get_session_vk_api(change_lp(prefix_base))
    msgs = get_msg(vkapp, -168171570, 0, 50)
    for sample in msgs:
        sample = clear_copy_history(sample)
        link = ''.join(map(str, ('wall', sample['owner_id'], '_', sample['id'])))
        if link not in base['links']['krugozor']:
            sample['text'] = ''.join(map(str, (conf[base['prefix']]['podpisi']['zagolovok']['krugozor'],
                                               avtortut(sample),
                                               conf[base['prefix']]['podpisi']['heshteg']['krugozor'],
                                               conf[base['prefix']]['podpisi']['final'])))
            if upload_post_to_main_group(vkapp, sample, base):
                base['links']['krugozor'].append(link)
                while len(base['links']['krugozor']) > 50:
                    del base['links']['krugozor'][0]
                writejson(bases + base['prefix'] + fbase, base)
                break
