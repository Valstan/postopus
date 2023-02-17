import os

from aiogram import Bot
from aiogram.types import InputMediaPhoto, FSInputFile

from bin.rw.get_image import get_image
from bin.rw.get_link_image_select_size import get_link_image_select_size
from bin.rw.get_msg import get_msg
from bin.utils.driver_tables import save_table
from bin.utils.lip_of_post import lip_of_post
from bin.utils.search_text import search_text
from config import session

bot = Bot(token=session['TELEGA_TOKEN_VALSTANBOT'])


async def send_text_post(text):
    await bot.send_message(session['post_group_telega'], text)


async def send_media_post(media):
    await bot.send_media_group(session['post_group_telega'], media)
    await bot.session.close()


async def post_to_telegram():
    posts = get_msg(session['post_group_vk'], 0, 20)

    # Убираем ненужные посты
    clear_posts = []
    for sample in posts:
        if 'copy_history' in sample or \
            'views' not in sample or \
            lip_of_post(sample) in session['work'][session['name_session']]['lip'] or \
            not search_text(['Новости', 'афиша'], sample['text']):
            continue
        if search_text(['афиша'], sample['text']):
            sample['views']['count'] += 20000
        clear_posts.append(sample)

    clear_posts.sort(key=lambda x: x['views']['count'], reverse=True)

    caption_text = True
    for sample in clear_posts:
        media = []
        media_files = []
        count_attach = 0

        if 'attachments' not in sample or len(sample['attachments']) < 1:
            if len(sample['text']) > 4096:
                await send_text_post(sample['text'][:4096])
                await send_text_post(sample['text'][4096:])
            else:
                await send_text_post(sample['text'])
            session['work'][session['name_session']]['lip'].append(lip_of_post(sample))
            break

        # Если текст длинный, то публикуем его сразу или обрезаем и публикуем сразу
        if len(sample['text']) > 1024:
            if len(sample['text']) > 4096:
                await send_text_post(sample['text'][:4096])
                await send_text_post(sample['text'][4096:])
            else:
                await send_text_post(sample['text'])
            caption_text = False

        # Смотрим, есть ли в посте фото, и если есть то публикуем, если текст не был опубликован (flag=True),
        # то прикрепляем его к первому фото
        for attach in sample['attachments']:
            if count_attach == 10:
                break
            if 'photo' in attach:
                url_photo = get_link_image_select_size(attach['photo']['sizes'], 300, 1281)
                if get_image(url_photo, f'telega_image_{count_attach}.jpg'):
                    if caption_text:
                        media.append(InputMediaPhoto(media=FSInputFile(f'telega_image_{count_attach}.jpg'), caption=sample['text']))
                        media_files.append(f'telega_image_{count_attach}.jpg')
                        count_attach += 1
                        caption_text = False
                    else:
                        if get_image(url_photo, f'telega_image_{count_attach}.jpg'):
                            media.append(InputMediaPhoto(media=FSInputFile(f'telega_image_{count_attach}.jpg')))
                            media_files.append(f'telega_image_{count_attach}.jpg')
                            count_attach += 1

        session['work'][session['name_session']]['lip'].append(lip_of_post(sample))

        if media:
            await send_media_post(media)
            for i in media_files:
                os.remove(i)
            break

        # Если caption_text нет, значит какой-то текст был распечатан, выходим, даже если фотки не прошли.
        if not caption_text:
            break

    save_table(session['name_session'])


if __name__ == '__main__':
    # asyncio.run(main())
    pass
