from bin.utils.bags import bags
from bin.utils.text_to_mono_text import text_to_mono_text
from bin.utils.url_of_post import url_of_post
from config import session


def sort_black_list(sample):
    sample_text = text_to_mono_text(sample['text'])
    for string in session['delete_msg_blacklist']:
        string = string.replace('"', '')
        string = string.lower()
        if string in sample_text:
            bags(sample_text=sample['text'], string=string, url=url_of_post(sample))
            return True


if __name__ == '__main__':
    pass
