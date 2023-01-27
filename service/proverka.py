group_list = -158787639, -86517261, -89083141, -158787639, -86517261, -89083141, -158787639, -86517261, -89083141,\
    -158787639, -86517261, -89083141, -158787639, -86517261, -89083141,-158787639, -86517261, -89083141, -158787639,\
    -86517261, -89083141, -158787639, -86517261, -89083141, -158787639, -86517261, -89083141, -158787639, -86517261,\
    -89083141, -158787639, -86517261, -89083141,
group_ids_str = ''
if len(group_list) > 24:
    batch = 24
    while len(group_list):
        if len(group_list) < batch:
            batch = len(group_list)
        group_ids_str += ','.join(map(str, group_list[:batch])) + ','
        group_list = group_list[batch:]
else:
    group_ids_str = ','.join(map(str, group_list)) + ','

pass

#
# import config
# from bin.rw.get_session_vk_api import get_session_vk_api
#
# session = config.session  # Берем сессию из конфига
# session.update({"token": session['VK_TOKEN_VALSTAN']})
# get_session_vk_api()
#
# new_posts = session['tools'].get_all(method='wall.get', max_count=100, limit=100,
#                                      values={'owner_id': [-158787639, -86517261, -89083141]})['items']
# pass
