import asyncio

from aiogram import Bot

from config import session

API_TOKEN = session['TELEGA_TOKEN_VALSTANBOT']
CHANNEL_ID = "@malmyzh_info"  # это должен быть int, например -1001144616980 malmyzh_info

bot = Bot(token=API_TOKEN)


async def send_message(channel_id: str, media: list):
    await bot.send_media_group(channel_id, media)


async def main(media, text):
    for sample in afisha_vk:
        if re.search("афишамалмыж", sample['text'], re.M | re.I):
            flag = True
            for foto in sample['attachments']:
                if flag:
                    media.append(
                        InputMediaPhoto(media=afisha_m[str(foto['photo']['id'])], caption=sample['text']))
                    flag = False
                else:
                    media.append(InputMediaPhoto(media=afisha_m[str(foto['photo']['id'])]))
    await send_message(CHANNEL_ID, media)


async def post_to_telega(msg):
    media = []
    if msg['attachments']:
        media.append()

    asyncio.run(main(media, text))


if __name__ == '__main__':
    # asyncio.run(main())
    pass
