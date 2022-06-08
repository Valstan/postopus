def post_msg(vk_app, group, text_send, attachments):
    vk_app.wall.post(owner_id=group,
                     from_group=1,
                     message=text_send,
                     attachments=attachments)


if __name__ == '__main__':
    pass
