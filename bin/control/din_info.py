import os

from aiogram import Bot
from aiogram.types import InputMediaPhoto, FSInputFile

from bin.rw.get_image import get_image
from bin.rw.get_link_image_select_size import get_link_image_select_size
from bin.utils.driver_tables import save_table
from bin.utils.lip_of_post import lip_of_post
from config import session


async def send_text_post(text, post_group_telega, bot):
    await bot.send_message(post_group_telega, text)


async def send_media_post(media, post_group_telega, bot):
    await bot.send_media_group(post_group_telega, media)


async def din_info(posts):
    name_din_info = "@+D4OeTb35c5ZlMDZi"

    # Открываем сессию Бота
    bot = Bot(token=session['TELEGA_TOKEN_VALSTANBOT'])

    for post in posts:
        # Если текст слишком длинный, то публикуем его сразу или режем на части и публикуем сразу
        if len(post['text']) > 1024:
            if len(post['text']) > 4096:
                while post['text']:
                    await send_text_post(post['text'][:4096], name_din_info, bot)
                    post['text'] = post['text'][4096:]
            else:
                await send_text_post(post['text'], name_din_info, bot)
            post['text'] = ''

        # Если есть фотки
        if 'attachments' in post and len(post['attachments']) > 0:

            media_files = []
            media = []
            count_attach = 0

            for attach in post['attachments']:
                if count_attach == 10:
                    break
                if 'photo' in attach:
                    url_photo = get_link_image_select_size(attach['photo']['sizes'], 300, 1281)
                    if get_image(url_photo, f'telega_image_{count_attach}.jpg'):
                        if post['text']:  # Если еще остался текст, то прикрепляем к первой фотке
                            media.append(InputMediaPhoto(media=FSInputFile(f'telega_image_{count_attach}.jpg'),
                                                         caption=post['text']))
                            media_files.append(f'telega_image_{count_attach}.jpg')
                            count_attach += 1
                            post['text'] = ''
                        else:
                            media.append(InputMediaPhoto(media=FSInputFile(f'telega_image_{count_attach}.jpg')))
                            media_files.append(f'telega_image_{count_attach}.jpg')
                            count_attach += 1

            if media:
                await send_media_post(media, name_din_info, bot)
                for i in media_files:
                    os.remove(i)

        # Если текст был короткий и без фоток, то печатаем его
        if post['text']:
            await send_text_post(post['text'], name_din_info, bot)

    # Закрываем сессию Бота
    await bot.session.close()

    session['work'][session['name_session']][f"lip_{name_din_info}"].append(lip_of_post(posts[0]))
    save_table(session['name_session'])


if __name__ == '__main__':
    # asyncio.run(main())
    pass
