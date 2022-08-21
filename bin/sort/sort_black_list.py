def sort_black_list(delete_msg_blacklist, msg):
    msg = msg.replace('"', '')
    msg = msg.replace('\n', '')
    msg = msg.lower()
    for sample in delete_msg_blacklist:
        sample = sample.replace('"', '')
        sample = sample.lower()
        if sample in msg:
            print(f"______!!! АХТУНГ !!!________\nВ черном списке, сообщение не будет опубликовано\n{sample}\n{msg}")
            return True


if __name__ == '__main__':
    pass
