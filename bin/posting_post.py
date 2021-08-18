from bin.rw.upload_post_to_main_group import upload_post_to_main_group


def posting_post(vkapp, session, msg_list):
    for sample in msg_list:
        if upload_post_to_main_group(vkapp, session['post_group']['key'], sample):
            skleika = str(sample['owner_id']) + str(sample['id'])
            session[session['name_session']]['lip'].append(skleika)
            break
    return session


if __name__ == '__main__':
    pass
