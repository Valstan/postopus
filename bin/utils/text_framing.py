from bin.utils.avtortut import avtortut


def text_framing(heading, body, hashtag, final, source=None):
    if source:
        return ''.join(map(str, heading, avtortut(body), hashtag, final))
    return ''.join(map(str, heading, body, hashtag, final))
