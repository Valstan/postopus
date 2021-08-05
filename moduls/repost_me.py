from bases.logpass import login, password
from config import bases, fbase, conf
from moduls.read_write.get_msg import get_msg
from moduls.read_write.get_session_vk_api import get_session_vk_api
from moduls.read_write.get_json import getjson
from moduls.read_write.write_json import writejson


def post_me():
    base = getjson(bases + 'm' + fbase)
    if 'repost' not in base['links']:
        base['links']['repost'] = []
    vkapp = get_session_vk_api(login['valstan'], password['valstan'])
    new_posts = get_msg(vkapp, conf['m']['post_group']['key'], 10, 10)
    sample_template_repost = ''
    for sample in new_posts:
        sample_template_repost = ''.join(map(str, ('wall', sample['owner_id'], '_', sample['id'])))
        if sample_template_repost not in base['links']['repost']:
            if conf['m']['podpisi']['heshteg']['reklama'] not in sample['text'] and \
                    conf['m']['podpisi']['heshteg']['music'] not in sample['text']:
                break
        sample_template_repost = ''
    if sample_template_repost:
        try:
            vkapp.wall.repost(object=sample_template_repost)
        except:
            pass
        base['links']['repost'].append(sample_template_repost)
        while len(base['links']['repost']) > 30:
            del base['links']['repost'][0]
        writejson(bases + 'm' + fbase, base)


if __name__ == '__main__':
    post_me()
