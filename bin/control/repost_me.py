from bin.utils.driver import load_table, save_table
from bin.rw.change_lp import change_lp
from bin.rw.get_msg import get_msg
from bin.rw.get_session_vk_api import get_session_vk_api


def repost_me(session):
    for session['name_session'] in session['repost_accounts']:
        session = load_table(session, session['name_session'])
        vkapp = get_session_vk_api(change_lp(session))
        new_posts = get_msg(vkapp, session['post_group']['key'], 0, 15)
        link = ''
        for sample in new_posts:
            link = ''.join(map(str, ('https://vk.com/wall', sample['owner_id'], '_', sample['id'])))
            if link not in session[session['name_session']]['lip']:
                if session['podpisi']['heshteg']['reklama'] not in sample['text']\
                    and\
                    session['podpisi']['heshteg']['music'] not in sample['text']:
                    break
            link = ''
        if link:
            try:
                vkapp.wall.repost(object=link)
            except:
                pass
            session[session['name_session']]['lip'].append(link)
            session['last_posts_counter'] = 10
            save_table(session, session['name_session'])


if __name__ == '__main__':
    pass
