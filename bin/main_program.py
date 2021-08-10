from config import bases, fbase, size_base_old_posts
from bin.parser import parser
from bin.rw.get_json import getjson
from bin.rw.upload_post_to_main_group import upload_post_to_main_group
from bin.rw.write_json import writejson
from bin.sort.sort_po_foto import sort_po_foto


def main_program(vkapp, name_novost, prefix_base):
    base = getjson(bases + prefix_base + fbase)
    base, msg_list = parser(vkapp, base, name_novost)
    if msg_list:
        for sample in msg_list:
            if upload_post_to_main_group(vkapp, sample, base):
                skleika = str(sample['owner_id']) + str(sample['id'])
                base['lip'].append(skleika)
                while len(base['lip']) > size_base_old_posts:
                    del base['lip'][0]
                sample, histo = sort_po_foto(sample, base)
                if histo:
                    base['hash'].append(histo)
                    while len(base['hash']) > size_base_old_posts:
                        del base['hash'][0]
                writejson(bases + base['prefix'] + fbase, base)
                return True
    writejson(bases + base['prefix'] + fbase, base)
    return False


if __name__ == '__main__':
    pass
