from bin.utils.url_of_post import url_of_post


def sort_black_list(delete_msg_blacklist, msg, bags="0"):
    msg = msg.replace('"', '')
    msg = msg.replace('\n', '')
    msg = msg.lower()
    for sample in delete_msg_blacklist:
        sample = sample.replace('"', '')
        sample = sample.lower()
        if sample in msg:
            if bags == "3":
                print(f"____!!! Слово в черном списке !!!______\n"
                      f"{sample}\n"
                      f"Не будет опубликован пост:\n"
                      f"{msg}\n"
                      f"{url_of_post(sample)}")
            return True


if __name__ == '__main__':
    pass
