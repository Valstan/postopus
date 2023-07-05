from vk_api import VkApi

import config
from bin.rw.get_msg import get_msg
from bin.utils.clear_copy_history import clear_copy_history

session = config.session

session.update({"token": session['VK_TOKEN_DRAN']})
vk_session = VkApi(token=session['token'])
session['vk_app'] = vk_session.get_api()
new_posts = get_msg(-179037590, 0, 100)
sample_clear = []
for sample in new_posts:
    template = clear_copy_history(sample)
    # if template['owner_id'] not in (-179037590, -162751110):
    sample_clear.append(template)
pass
print('Конец')


