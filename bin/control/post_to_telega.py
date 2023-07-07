import os

from aiogram import Bot
from aiogram.types import InputMediaPhoto, FSInputFile

from bin.rw.get_image import get_image
from bin.rw.get_link_image_select_size import get_link_image_select_size
from bin.rw.get_msg import get_msg
from bin.utils.clear_copy_history import clear_copy_history
from bin.utils.driver_tables import save_table
from bin.utils.lip_of_post import lip_of_post
from bin.utils.search_text import search_text
from config import session


async def send_text_post(text, post_group_telega, bot):
    await bot.send_message(post_group_telega, text)


async def send_media_post(media, post_group_telega, bot):
    await bot.send_media_group(post_group_telega, media)


async def post_to_telegram():
    for twins in session['all_telega_group']:

        posts = get_msg(twins[0], 0, 20)

        # Набираем правильные посты
        clear_posts = []
        for sample in posts:
            if lip_of_post(sample) in session['work'][session['name_session']][f"lip_{twins[1]}"]:
                continue
            # if 'malmyzh_info' in twins[1]:
            # if search_text(['АФИША ВАКАНСИЙ'], sample['text']):
            #     continue
            # if search_text(['афиша'], sample['text']):
            #     sample['views']['count'] += 20000

            # Вытягиваем если есть репосты и снова проверяем на повтор по номеру поста
            sample = clear_copy_history(sample)
            if lip_of_post(sample) in session['work'][session['name_session']][f"lip_{twins[1]}"] \
                or sample['owner_id'] == -179037590 \
                or search_text(['ОбъявленияМалмыж',
                                'УраПерерывчикМалмыж',
                                'КиноМалмыж'], sample['text']):
                continue

            if 'views' not in sample:
                sample['views'] = {'count': 5}

            clear_posts.append(sample)

        if not clear_posts:
            continue

        if len(clear_posts) > 1:
            clear_posts.sort(key=lambda x: x['views']['count'], reverse=True)

        # Публикуем тупо самый первый верхний пост.
        # Вырезаю из поста ссылки на источник
        text_list = clear_posts[0]['text'].split(sep="\n", maxsplit=-1)
        clear_posts[0]['text'] = ''
        for i in text_list:
            if ("[http" and '|') not in i:
                clear_posts[0]['text'] += i + "\n"
        clear_posts[0]['text'] = clear_posts[0]['text'][:-1]

        # Открываем сессию Бота
        if 'malmyzh_info' in twins[1]:
            bot = Bot(token=session['TELEGA_TOKEN_AFONYA'])
        else:
            bot = Bot(token=session['TELEGA_TOKEN_VALSTANBOT'])

        # Если текст слишком длинный, то публикуем его сразу или режем на части и публикуем сразу
        if len(clear_posts[0]['text']) > 1024:
            if len(clear_posts[0]['text']) > 4096:
                while clear_posts[0]['text']:
                    await send_text_post(clear_posts[0]['text'][:4096], twins[1], bot)
                    clear_posts[0]['text'] = clear_posts[0]['text'][4096:]
            else:
                await send_text_post(clear_posts[0]['text'], twins[1], bot)
            clear_posts[0]['text'] = ''

        # Если есть фотки
        if 'attachments' in clear_posts[0] and len(clear_posts[0]['attachments']) > 0:

            media_files = []
            media = []
            count_attach = 0

            for attach in clear_posts[0]['attachments']:
                if count_attach == 10:
                    break
                if 'photo' in attach:
                    url_photo = get_link_image_select_size(attach['photo']['sizes'], 300, 1281)
                    if get_image(url_photo, f'telega_image_{count_attach}.jpg'):
                        if clear_posts[0]['text']:  # Если еще остался текст, то прикрепляем к первой фотке
                            media.append(InputMediaPhoto(media=FSInputFile(f'telega_image_{count_attach}.jpg'),
                                                         caption=clear_posts[0]['text']))
                            media_files.append(f'telega_image_{count_attach}.jpg')
                            count_attach += 1
                            clear_posts[0]['text'] = ''
                        else:
                            media.append(InputMediaPhoto(media=FSInputFile(f'telega_image_{count_attach}.jpg')))
                            media_files.append(f'telega_image_{count_attach}.jpg')
                            count_attach += 1

            if media:
                await send_media_post(media, twins[1], bot)
                for i in media_files:
                    os.remove(i)

        # Если текст был короткий и без фоток, то печатаем его
        if clear_posts[0]['text']:
            await send_text_post(clear_posts[0]['text'], twins[1], bot)

        # Закрываем сессию Бота
        await bot.session.close()

        session['work'][session['name_session']][f"lip_{twins[1]}"].append(lip_of_post(clear_posts[0]))
        save_table(session['name_session'])


if __name__ == '__main__':
    # asyncio.run(main())
    pass
