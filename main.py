import hashlib

from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ParseMode, InlineQueryResultArticle, InputTextMessageContent, InlineQuery
from aiogram import *

from responses.mining import MiningResponse
# from responses.vitex import VitexResponse
from parsers.mining import MiningParser
from parsers.vitex import VitexParser
from settings import Vitex, Mining
from logger_ import logger
from keys import TOKEN


__version__ = '0.1.0'

# /------ AIOGRAM BOT SETTINGS ------\ #
from tools import kill_markdown, get_time
from database import DataBase

db_v3_tests = DataBase('v3_tests')
storage = MemoryStorage()
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=storage)


def mining_queries(msg):
    return any(cmd in msg.query.split(' ') for cmd in Mining.INLINE_TRIGGERS)
def vitex_queries(msg):
    return any(cmd in msg.query.split(' ') for cmd in Vitex.INLINE_TRIGGERS)


# //-- WELCOME INLINE -- \\ #
@dp.inline_handler(lambda inline_query: inline_query.query == '')
async def inline_mining(inline_query: InlineQuery):
    result_id: str = hashlib.md5(inline_query.query.encode()).hexdigest()
    thumb_url = "https://i.ibb.co/Rgx9hv2/radar1.png"
    title = "EPIC-RADAR BOT COMMANDS:"
    lines = [
        f"mining <algo> <hashrate> <units>",
        f"price"
        ]

    item = InlineQueryResultArticle(
        id=result_id,
        title=title,
        description='\n'.join(lines),
        thumb_url=thumb_url,
        input_message_content=InputTextMessageContent('xx', parse_mode=ParseMode.MARKDOWN)
        )
    await bot.answer_inline_query(inline_query.id, results=[item], cache_time=1)


# //-- MINING INLINE --\\ #
@dp.inline_handler(lambda inline_query: mining_queries(inline_query))
async def inline_mining(inline_query: InlineQuery):
    result_id: str = hashlib.md5(inline_query.query.encode()).hexdigest()
    user_query = MiningParser(message=inline_query.query)
    response = MiningResponse(user_query)

    item = InlineQueryResultArticle(
        id=result_id,
        title=response.inline_title,
        description=response.inline_response,
        thumb_url=response.thumb_url,
        input_message_content=InputTextMessageContent(response.chat_response, parse_mode=ParseMode.MARKDOWN)
        )
    await bot.answer_inline_query(inline_query.id, results=[item], cache_time=1)


# //-- VITEX/TRADING INLINE --\\ #
@dp.inline_handler(lambda inline_query: vitex_queries(inline_query))
async def inline_vitex(inline_query: InlineQuery):
    result_id: str = hashlib.md5(inline_query.query.encode()).hexdigest()
    user_query = VitexParser(message=inline_query.query)
    # response = VitexResponse(user_query)
    usd = round(float(user_query.response['price']['usd']), 2)
    btc = "{:.8f}".format(float(user_query.response['price']['btc']))
    change = user_query.response['change']['24h_percentage']
    volume_epic = user_query.response['volume']['epic']
    volume_btc = user_query.response['volume']['btc']
    url = "https://x.vite.net/trade?symbol=EPIC-002_BTC-000"

    title = f"EPIC: {usd} USD"
    body = f"{btc} BTC ({float(change) * 100}%)\n24H Volume: {volume_epic} EPIC | {volume_btc} BTC"

    item = InlineQueryResultArticle(
        id=result_id,
        # url=url,
        title=title,
        description=body,
        thumb_url="https://i.ibb.co/j3QGQ3G/tg-bot-vitex-logo.png",
        input_message_content=InputTextMessageContent('\n'.join([f"*{title}*", body]), parse_mode=ParseMode.MARKDOWN)
        )
    # don't forget to set cache_time=1 for testing (default is 300s or 5m)
    await bot.answer_inline_query(inline_query.id, results=[item], cache_time=100)


# //-- V3 TEST MEMBERS REGISTER -- \\ #
@dp.message_handler(commands=['add_to_bees', 'add_to_rabbits', 'add_to_owls'])
async def register_test_members(message: types.Message):
    cmd = message.get_command()
    team = cmd.split('_')[-1]
    icons = {'bees': '🐝', 'rabbits': '🐇', 'owls': '🦉'}

    # If @username not specified use sender's @username
    if '@' in message.text:
        user = message.text.split('@')[-1]
    else:
        user = message.from_user.username

    # Prepare dict to save to database
    data = {'time': get_time(), 'username': user, 'team': team,  'msg_id': message.message_id}

    # If @username is not found in DB create new record
    if user not in db_v3_tests.get_all().keys():
        db_v3_tests.save(f"{user}", data)
        response = f"<b>@{user}</b> added to {team.capitalize()} {icons[team]} Team!"

    # If @username already exists show proper message
    else:
        team = [k for k, v in db_v3_tests.get_all().items() if user in k]
        team = db_v3_tests.get(team[0])['team']
        response = f"<b>@{user}</b> already in {team.capitalize()} {icons[team]} Team!"

    await message.reply(response, parse_mode=ParseMode.HTML, reply=False)


# //-- V3 TEST MEMBERS LIST -- \\ #
@dp.message_handler(commands=['teams'])
async def list_test_members(message: types.Message):
    icons = {'bees': '🐝', 'rabbits': '🐇', 'owls': '🦉'}

    users = [values for user, values in db_v3_tests.get_all().items() if isinstance(values, dict)]
    print(users)

    teams = {'bees': [], 'rabbits': [], 'owls': []}

    for user in users:
        teams[user['team']].append(user['username'])

    response = f"👤 Registered volunteers: {len(users)}\n\n" \
               f"{icons['bees']}Bees: {len(teams['bees'])}\n" \
               f"{icons['rabbits']}Rabbits: {len(teams['rabbits'])}\n" \
               f"{icons['owls']}Owls: {len(teams['owls'])}"

    await message.reply(response, parse_mode=ParseMode.HTML, reply=False)


# //-- V3 TEST MEMBERS REMOVE -- \\ #
@dp.message_handler(commands=['delete', 'del', 'remove'])
async def remove_test_members(message: types.Message):
    cmd = message.get_command()
    user = message.from_user.username
    icons = {'bees': '🐝', 'rabbits': '🐇', 'owls': '🦉'}

    # If @username is not found in DB show proper message
    if user not in db_v3_tests.get_all().keys():
        response = f"ℹ️ <b>@{user}</b> have no team assigned."

    # If @username exists delete that record
    else:
        username = [k for k, v in db_v3_tests.get_all().items() if user in k]
        team = db_v3_tests.get(username[0])['team']
        response = f"❗️<b>@{user}</b> removed from {team.capitalize()} {icons[team]} Team!"
        db_v3_tests.delete(user)

    await message.reply(response, parse_mode=ParseMode.HTML, reply=False)


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
