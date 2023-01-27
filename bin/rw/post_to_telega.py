import asyncio

from aiogram import Bot

from config import session

API_TOKEN = session['TELEGA_TOKEN_VALSTANBOT']
CHANNEL_ID = "@malmyzh_info"  # это должен быть int, например -1001144616980 malmyzh_info

bot = Bot(token=API_TOKEN)


async def send_message(channel_id: str, media: list, text: str):
    await bot.send_media_group(channel_id, text)


async def main(media, text):
    await send_message(CHANNEL_ID, media, text)


async def post_to_telega(media, text):
    asyncio.run(main(media, text))


if __name__ == '__main__':
    # asyncio.run(main())
    pass
