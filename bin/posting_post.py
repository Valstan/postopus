from bin.rw.upload_post_to_main_group import upload_post_to_main_group
from bin.sort.sort_po_foto import sort_po_foto


def posting_post(vkapp, session, msg_list):
    for sample in msg_list:
        if upload_post_to_main_group(vkapp, session['post_group']['key'], sample):
            skleika = str(sample['owner_id']) + str(sample['id'])
            session[session['name_session']]['lip'].append(skleika)
            session, sample = sort_po_foto(session, sample)
            break
    return session


if __name__ == '__main__':
    pass
