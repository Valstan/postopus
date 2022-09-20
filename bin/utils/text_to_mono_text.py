def text_to_mono_text(txt):
    txt = txt.replace('\n', ' ')
    txt = txt.replace('"', ' ')
    txt = txt.replace('  ', ' ')
    txt = txt.lower()
    return txt
