def get_attach(msg):
    if 'attachments' in msg:
        attach = ''
        count = 0
        for sample in msg['attachments']:
            type_attach = sample['type']
            if type_attach == 'link':
                # return sample[type_attach]['url']
                continue
            elif type_attach == 'photos_list':
                attach += ''.join(map(str, (type_attach, sample[type_attach], ',')))
                return attach[:-1], 10
            else:
                attach += ''.join(map(str, (type_attach, sample[type_attach]['owner_id'],
                                            '_', sample[type_attach]['id'], ',')))
                count += 1
        return attach[:-1], count
    else:
        return ''


if __name__ == '__main__':
    pass
