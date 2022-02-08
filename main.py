import hashlib

from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ParseMode, InlineQueryResultArticle, InputTextMessageContent, InlineQuery
from aiogram import *

from responses.mining import MiningResponse
# from responses.vitex import VitexResponse
from parsers.mining import MiningParser
from parsers.vitex import VitexParser
from settings import Vitex, Mining, V3tests
from database import DataBase
from logger_ import logger
from tools import get_username, get_teams, valid_channel, get_time
from keys import TOKEN


__version__ = '0.1.0'

# /------ AIOGRAM BOT SETTINGS ------\ #
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
async def inline_welcome(inline_query: InlineQuery):
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


# //-- MINING PRIVATE -- \\ #
@dp.message_handler(lambda message: any(x in message.text.split(' ') for x in Mining.ALGO_PATTERNS))
async def private_mining(message: types.Message):
    msg = message['text']
    user_query = MiningParser(message=msg)
    response = MiningResponse(user_query)

    await message.reply(response.chat_response, parse_mode=ParseMode.MARKDOWN, reply=False)


# --------------------#
#   V3 TEST SECTION   #
# --------------------#


# //-- MEMBERS REGISTER -- \\ #
@dp.message_handler(commands=['add_to_bees', 'add_to_rabbits', 'add_to_owls'])
async def register_test_members(message: types.Message):
    if valid_channel(message.chat.id, V3tests):
        cmd = message.get_command()
        team = cmd.split('_')[-1]
        icons = V3tests.TEAM_ICONS
        username, mention = get_username(message).values()

        # Prepare dict to save to database
        data = {'username': username,
                'team': team,
                'time': get_time(),
                'msg_id': message.message_id,
                'mention': mention}

        # If user is not found in DB create new record
        if username not in db_v3_tests.get_all().keys():
            db_v3_tests.save(f"{username}", data)
            response = f"*{mention}* added to {team.capitalize()} {icons[team]} Team\!"

        # If @username already exists show proper message
        else:
            team = [k for k, v in db_v3_tests.get_all().items() if username in k]
            team = db_v3_tests.get(team[0])['team']
            response = f"*{mention}* already in {team.capitalize()} {icons[team]} Team\!"

        await message.reply(response.replace('_', '\_'), parse_mode=ParseMode.MARKDOWN_V2, reply=False)


# //-- MEMBERS REMOVE -- \\ #
@dp.message_handler(commands=['delete', 'del', 'remove'])
async def remove_test_members(message: types.Message):
    if valid_channel(message.chat.id, V3tests):
        username, mention = get_username(message).values()
        icons = V3tests.TEAM_ICONS

        # If @username is not found in DB show proper message
        if username not in db_v3_tests.get_all().keys():
            response = f"ℹ️ {mention} have no team assigned\."

        # If @username exists delete that record
        else:
            username_ = [k for k, v in db_v3_tests.get_all().items() if username in k]
            team = db_v3_tests.get(username_[0])['team']
            db_v3_tests.delete(username)
            response = f"❗️{mention} removed from {team.capitalize()} {icons[team]} Team\!"

        print(response)
        await message.reply(response.replace('_', '\_'), parse_mode=ParseMode.MARKDOWN_V2, reply=False)


# //-- MEMBERS LIST -- \\ #
@dp.message_handler(commands=['teams'])
async def list_test_members(message: types.Message):
    if valid_channel(message.chat.id, V3tests):
        icons = V3tests.TEAM_ICONS
        teams = get_teams(database=db_v3_tests)
        print(teams)

        response = f"<b>🏆 Registered Volunteers:</b>\n\n" \
                   f"{icons['bees']} Bees: {len(teams['bees'])}\n" \
                   f"{icons['rabbits']} Rabbits: {len(teams['rabbits'])}\n" \
                   f"{icons['owls']} Owls: {len(teams['owls'])}"

        await message.reply(response, parse_mode=ParseMode.HTML, reply=False)


# //-- TAG TEAMS -- \\ #
@dp.message_handler(commands=['tag', 'all', 'call'])
async def call_test_members(message: types.Message):
    response = None
    if valid_channel(message.chat.id, V3tests):
        teams = get_teams(database=db_v3_tests)
        tagged = message.get_command(pure=True)

        if tagged in 'all':
            response_ = []
            for team in teams.values():
                for user in team:
                    response_.append(user['mention'])
            response = ' '.join(response_)

        else:
            tag = message.get_args()
            if tag in teams.keys():
                response = ' '.join([user['mention'] for user in teams[tag]])

        if response:
            print('TAGGING: ', response)
            await message.reply(response.replace('_', '\_'), parse_mode=ParseMode.MARKDOWN_V2, reply=False)


# //-- ADMIN USERS LIST (PRINT) -- \\ #
@dp.message_handler(commands=['ad_list'])
async def list_test_members_admin(message: types.Message):
    if valid_channel(message.chat.id, V3tests):
        users = [values for user, values in db_v3_tests.get_all().items() if isinstance(values, dict)]
        for user in users:
            print(user)
        try: await bot.delete_message(message.chat.id, message.message_id)
        except Exception: pass

# //-- ADMIN MEMBERS REMOVE (PRINT) -- \\ #
@dp.message_handler(commands=['ad_rem'])
async def remove_test_members_admin(message: types.Message):
    if valid_channel(message.chat.id, V3tests):
        icons = V3tests.TEAM_ICONS
        username, mention = get_username(message).values()

        if username not in db_v3_tests.get_all().keys():
            response = f"ℹ️ {mention} have no team assigned."

        else:
            username_ = [k for k, v in db_v3_tests.get_all().items() if username in k]
            team = db_v3_tests.get(username_[0])['team']
            response = f"❗️*{mention}* removed from {team.capitalize()} {icons[team]} Team!"
            db_v3_tests.delete(username)

        try: await bot.delete_message(message.chat.id, message.message_id)
        except Exception: pass
        print(response)


# //-- ADMIN GET CHAT ID -- \\ #
@dp.message_handler(commands=['get_id'])
async def get_chat_ID(message: types.Message):
    chat_id = message.chat.id
    await message.reply(chat_id, parse_mode=ParseMode.HTML, reply=False)


# /------ START MAIN LOOP ------\ #
if __name__ == '__main__':
    logger.info("starting")
    executor.start_polling(dp, skip_updates=True)
