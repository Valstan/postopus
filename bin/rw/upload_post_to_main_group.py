from bin.r_w.get_attach import get_attach
from bin.r_w.post_msg import post_msg


def upload_post_to_main_group(vkapp, group_id, msg):
    attachments = ''
    if 'attachments' in msg:
        attachments = get_attach(msg)
    try:
        post_msg(vkapp,
                 group_id,
                 msg['text'],
                 attachments)
    except:
        return False
    return True
