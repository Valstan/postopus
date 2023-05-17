def url_of_post(sample):
    return ''.join(map(str, ('https://vk.com/wall', sample['owner_id'], '_', sample['id'])))
