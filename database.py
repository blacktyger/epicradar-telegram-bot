import shelve
import time
import sys
import os

from logger_ import logger


PROJECT_DIR = os.path.dirname(sys.argv[0])
DB_DIR_NAME = 'db'
DB_DIR_PATH = os.path.join(PROJECT_DIR, DB_DIR_NAME)

class DataBase:
    """Class to manage user and app settings in a form of very basic pickled based database"""
    defaults = {'created': time.time()}

    def __init__(self, db_name):
        self.name = db_name
        self.dir = DB_DIR_PATH
        self.file = os.path.join(DB_DIR_PATH, self.name)
        self._load()

    def _load(self) -> None:
        if not os.path.isdir(self.dir):
            os.mkdir(self.dir)

        if not os.path.exists(self.file):
            for key, value in self.defaults.items():
                self._save(key, value)
            logger.info(f'Database({self}) created')
        else:
            logger.debug(f'Database({self}) loaded successfully')

    def _save(self, key: str, value: str) -> None:
        with shelve.open(self.file, 'c') as db:
            db[key] = value
            logger.debug(f'{key} - {value} saved to db({self}')

    def _read(self, key: str, get_all: bool = False):
        with shelve.open(self.file, 'r') as db:
            if get_all:
                return dict(db)
            if key in db.keys():
                logger.debug(f'{key} - {db[key]} found in db({self}')
                return db[key]
            else:
                logger.debug(f'{key} - NOT found in db({self}')
                return None

    def delete(self, key):
        with shelve.open(self.file, 'c') as db:
            db.pop(key)
            logger.debug(f'{key} deleted from db({self}')

    def save(self, key: str, value):
        self._save(key, value)

    def get(self, key: str):
        return self._read(key)

    def get_all(self):
        print(self._read('', get_all=True))
        return self._read('', get_all=True)

    def __repr__(self):
        return f"Database({self.name})"