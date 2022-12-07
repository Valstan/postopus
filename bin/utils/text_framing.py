from bin.utils.avtortut import avtortut


def text_framing(heading, body, hashtag, final, body_source=None):
    if body_source:
        body = avtortut(body, "\n")
    return ''.join(map(str, [heading, body, '\n', hashtag, final]))
