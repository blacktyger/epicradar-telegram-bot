import datetime
import time

from aiogram import types


def kill_markdown(string):
    return string.replace('*', '')


def get_teams(database):
    """Return dict with all members according tot their teams"""
    users = [values for user, values in database.get_all().items() if isinstance(values, dict)]
    teams = {'bees': [], 'rabbits': [], 'owls': []}

    for user in users:
        teams[user['team']].append(user)

    return teams


def valid_channel(_id, database):
    """Validate channel ID before sending"""
    _id = str(_id).split('-')[-1]
    return _id in database.TESTERS_CHANNEL_ID or \
           _id in database.TEST_CHANNEL_ID or \
           _id in database.TEST_DEV_CHANNEL_ID


def get_username(message: types.Message) -> dict:
    """Return dict with User username and User mention string"""
    mentioned = len(message.entities) == 2

    if mentioned:
        # Return user mentioned by sender
        user = message.entities[-1].user

        if user:
            if user.username:
                username = user.username
                mention = user.mention
            else:
                username = user.first_name
                mention = user.get_mention(username)
        else:
            username = message.parse_entities().split('@')[-1]
            mention = message.parse_entities().split(' ')[-1]

    else:
        # Return message sender user
        if message.from_user.username:
            username = message.from_user.username
        else:
            username = message.from_user.first_name
        mention = message.from_user.mention

    return {'username': username, 'mention': mention}


def get_time(pattern="%d/%m %H:%M"):
    """Return datetime object as string"""
    return datetime.datetime.now().strftime(pattern)


def timeit(method):
    """Help to measure performance"""

    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts) * 1000)
        else:
            print('%r  %2.2f ms' % (method.__name__, (te - ts) * 1000))
        return result

    return timed
