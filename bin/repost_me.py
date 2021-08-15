from bin.driver import load_table, save_table
from bin.rw.change_lp import change_lp
from bin.rw.get_msg import get_msg
from bin.rw.get_session_vk_api import get_session_vk_api


def repost_me(session):

    for session['name_session'] in session['repost_accounts']:
        session = load_table(session, session['name_session'])
        vkapp = get_session_vk_api(change_lp(session))
        new_posts = get_msg(vkapp, session['post_group']['key'], 0, 15)
        sample_template_repost = ''
        for sample in new_posts:
            sample_template_repost = ''.join(map(str, ('wall', sample['owner_id'], '_', sample['id'])))
            if sample_template_repost not in session[session['name_session']]['lip']:
                if session['podpisi']['heshteg']['reklama'] not in sample['text'] and \
                        session['podpisi']['heshteg']['music'] not in sample['text']:
                    break
            sample_template_repost = ''
        if sample_template_repost:
            try:
                vkapp.wall.repost(object=sample_template_repost)
            except:
                pass
            session[session['name_session']]['lip'].append(sample_template_repost)
            while len(session[session['name_session']]['lip']) > 20:
                del session[session['name_session']]['lip'][0]
            save_table(session, session['name_session'])


if __name__ == '__main__':
    pass
