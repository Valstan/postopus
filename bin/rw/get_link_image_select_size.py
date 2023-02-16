def get_link_image_select_size(list_attach, mini, maxi):
    min_h = mini
    min_w = mini
    url = ''
    for i in list_attach:
        if min_h < i['height'] < maxi and min_w < i['width'] < maxi:
            min_h = i['height']
            min_w = i['width']
            url = i['url']
    return url
