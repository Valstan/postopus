import requests

from config import session


ACCESS_TOKEN = session['VK_TOKEN_VALSTAN']

groups_id = "-158787639,-86517261,-89083141,"  # В конце обязательно запятая иначе последнюю группу не получит

posts = requests.post('https://api.vk.com/method/execute.wallGet?groups_id=' + groups_id + '&access_token=' + ACCESS_TOKEN + '&v=5.131').json()


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
