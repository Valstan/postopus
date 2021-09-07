import re


def sort_black_list(delete_msg_blacklist, msg):
    msg = msg.replace('"', '')
    msg = msg.lower()
    for sample in delete_msg_blacklist:
        sample = sample.replace('"', '')
        sample = sample.lower()
        if re.search(sample, msg):
            return True


if __name__ == '__main__':
    pass
