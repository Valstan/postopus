def clear_copy_history(msg):

    if 'copy_history' in msg:
        new_msg = msg['copy_history'][0]
        new_msg['likes'] = msg['likes']
        new_msg['views'] = msg['views']
        return new_msg
    else:
        return msg
