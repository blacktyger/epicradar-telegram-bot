import hashlib

from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ParseMode, InlineQueryResultArticle, InputTextMessageContent, InlineQuery
from aiogram import *

from responses.mining import MiningResponse
# from responses.vitex import VitexResponse
from parsers.mining import MiningParser
from parsers.vitex import VitexParser
from settings import Vitex
from logger_ import logger
from keys import TOKEN


__version__ = '0.1.0'

# /------ AIOGRAM BOT SETTINGS ------\ #
from tools import kill_markdown

storage = MemoryStorage()
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=storage)


@dp.inline_handler(lambda inline_query: any(cmd in inline_query.query.split(' ') for cmd in PATTERNS.INLINE_TRIGGERS))
async def inline_mining(inline_query: InlineQuery):
    result_id: str = hashlib.md5(inline_query.query.encode()).hexdigest()
    user_query = MiningParser(message=inline_query.query)
    # response = MiningResponse(user_query)

    print(user_query.response['price'])
    item = InlineQueryResultArticle(
        id=result_id,
        title=response.title,
        description=kill_markdown('\n'.join(response.lines)),
        input_message_content=InputTextMessageContent(response.print, parse_mode=ParseMode.MARKDOWN)
        )
    # don't forget to set cache_time=1 for testing (default is 300s or 5m)
    await bot.answer_inline_query(inline_query.id, results=[item], cache_time=100)


@dp.inline_handler(lambda inline_query: any(cmd in inline_query.query.split(' ') for cmd in Vitex.PATTERNS.keys()))
async def inline_mining(inline_query: InlineQuery):
    result_id: str = hashlib.md5(inline_query.query.encode()).hexdigest()
    user_query = VitexParser(message=inline_query.query)
    response = VitexResponse(user_query)

    print(f"inline: {inline_query.query.split(' ')}")

    item = InlineQueryResultArticle(
        id=result_id,
        title=response.title,
        description=kill_markdown('\n'.join(response.lines)),
        input_message_content=InputTextMessageContent(response.print, parse_mode=ParseMode.MARKDOWN)
        )
    # don't forget to set cache_time=1 for testing (default is 300s or 5m)
    await bot.answer_inline_query(inline_query.id, results=[item], cache_time=100)


@dp.message_handler(lambda message: any(x in message.text.split(' ') for x in Mining.ALGO_PATTERNS))
async def private_mining(message: types.Message):
    msg = message['text']
    # a = MiningAnswer(icon='⚒', title='mining', message=msg)
    user_query = MiningParser(message=msg)
    response = MiningResponse(user_query)
    await message.reply('\n'.join(response.lines), parse_mode=ParseMode.MARKDOWN, reply=False)


# /------ START MAIN LOOP ------\ #
if __name__ == '__main__':
    logger.info("starting")
    executor.start_polling(dp, skip_updates=True)
