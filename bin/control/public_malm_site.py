import config
from bin.rw.read_posts import read_posts
from bin.sort.sort_old_date import sort_old_date
from bin.utils.bags import bags
from bin.utils.clear_copy_history import clear_copy_history
from bin.utils.driver_tables import load_table
from bin.utils.lip_of_post import lip_of_post
from bin.utils.url_of_post import url_of_post

session = config.session


def public_malm_site():

    for name_category, dict_ids in session['categories_ids'].iteritems():
        session['work'] = load_table(name_category)
        posts = read_posts(dict_ids, 20)
        result_posts = []
        for sample in posts:
            if lip_of_post(sample) in session['work'][name_category]['lip']:
                bags(sample_text=sample['text'], url=url_of_post(sample))
                continue

            # Проверяем пост на "старость"
            if not sort_old_date(sample):
                bags(sample_text=sample['text'], url=url_of_post(sample))
                session['work'][name_category]['lip'].append(lip_of_post(sample))
                continue

            sample = clear_copy_history(sample)
            if lip_of_post(sample) in session['work'][name_category]['lip']:
                bags(sample_text=sample['text'], url=url_of_post(sample))
                continue
