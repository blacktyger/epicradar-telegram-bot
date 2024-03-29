"""One place for all global settings used in different parts of code"""

from json import JSONDecodeError
from decimal import Decimal
from typing import Union
import itertools
import json
import time

import requests


class FEED_API:
    class EXPLORER_EPIC_TECH:
        API_URL = 'https://explorer.epic.tech/epic_explorer/v1'
        API_CALLS = {'latest_block': 'blockchain_block/latesblockdetails',
                     'block_by_height': 'blockchain_block'}
        PUBLIC_API_URL = "https://explorer.epic.tech/api?q="

    class EXPLORER_EPICMINE_ORG:
        API_URL = 'https://api.epicmine.org'

    class VITESCAN_IO:
        BASE_URL = "https://vitescan.io/"
        HOLDERS_API_URL = "vs-api/token?tokenId=tti_f370fadb275bc2a1a839c753&tabFlag=holders"


class MarketData:
    btc_feed_url = "https://blockchain.info"
    epic_feed_url = "https://api.coingecko.com/api/v3"

    def price_epic_vs(self, currency: str):
        symbol = currency.upper()
        if len(symbol) == 3:
            try:
                url = f"{self.epic_feed_url}/simple/price?ids=epic-cash&vs_currencies={symbol}"
                data = json.loads(requests.get(url).content)
                return Decimal(data['epic-cash'][symbol.lower()])
            except JSONDecodeError as er:
                print(er)
                return 0

    def price_btc_vs(self, currency: str):
        symbol = currency.upper()
        if len(symbol) == 3:
            try:
                url = f"{self.btc_feed_url}/ticker"
                data = json.loads(requests.get(url).content)
                return Decimal(data[symbol]['last'])
            except JSONDecodeError as er:
                print(er)
                return 0

    def currency_to_btc(self, value: Union[Decimal, float, int], currency: str):
        """Find bitcoin price in given currency"""
        symbol = currency.upper()
        if len(symbol) == 3:
            try:
                url = f'{self.btc_feed_url}/tobtc?currency={currency}&value={value}'
                data = json.loads(requests.get(url).content)
                return Decimal(data)
            except JSONDecodeError as er:
                print(er)
                return 0


class Vitex:
    EPIC_SYMBOL = "EPIC-002"
    BTC_SYMBOL = "BTC-000"
    DECIMAL = 10 ** 8

    INLINE_TRIGGERS = ['price', 'vitex']


class Mining:
    CALCULATOR_PERIODS = [1, 3, 7]
    PATTERNS = {
        'mining_algorithms': {
            'progpow': ('Pp', 'pp', 'progpow', 'ProgPow', 'PROGPOW', 'Progpow'),
            'randomx': ('Rx', 'rx', 'randomx', 'RANDOMX', 'RandomX', 'Randomx', 'randomX'),
            'cuckoo': ('cu', 'ck', 'co', 'cuckoo', 'Cuckoo', 'CUCKOO')
            },
        'units': {
            'hash': ('h', 'H'),
            'kilohash': ('kh', 'Kh', 'KH'),
            'megahash': ('mh', 'Mh', 'MH'),
            'gigahash': ('gh', 'Gh', 'GH')
            },
        'ticker': {
            'price': ('p', 'price')
            }
        }

    INLINE_TRIGGERS = ['mining', 'calculator', 'calc']
    ALGO_PATTERNS = list(itertools.chain(*PATTERNS['mining_algorithms'].values()))


class Database:
    API_URL = FEED_API.EXPLORER_EPIC_TECH.API_URL
    BLOCK_API = FEED_API.EXPLORER_EPIC_TECH.API_CALLS['latest_block']
    FILE_NAME = "db/block_data.json"

    def _fetch_explorer_data(self):
        url = f"{self.API_URL}/{self.BLOCK_API}"

        req = requests.Session()
        response = req.get(url, headers={'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"}).json()['response']

        data = {
            'height': response['block_height'],
            'network_hashrate': {
                'progpow': response['progpowhashrate'],
                'randomx': response['randomxhashrate'],
                'cuckoo': response['cuckoohashrate'],
                }
            }

        self._save_to_file(data)
        return data

    def _save_to_file(self, data: dict):
        with open(self.FILE_NAME, 'w') as file:
            file.write(json.dumps(data))

    def updater(self):
        while True:
            data = self._fetch_explorer_data()
            print(f"Get explorer data: {data}")
            time.sleep(60)

    def get_last_block_data(self):
        with open(self.FILE_NAME, 'r') as file:
            return json.loads(file.read())


class Blockchain:
    DECIMAL = 10 ** 8
    HALVINGS = [1157760, 1224000, 2275200]
    BLOCK_TIME = 60
    ALGORITHMS = ['cuckoo', 'progpow', 'randomx']
    BLOCKS_PER_DAY = Decimal(86400 / BLOCK_TIME)
    ALGORITHM_PERCENTAGE = {'cuckoo': 0.4, 'progpow': 0.48, 'randomx': 0.48}

    @staticmethod
    def get_exact_reward(height):
        if 698401 < height <= 1157760:
            return [8.0, 0.5328, 7.4672, 1157760]
        elif 1157761 < height <= 1224000:
            return [4.0, 0.2664, 3.7336, 2275200]
        elif 1224001 < height <= 1749600:
            return [4.0, 0.2220, 3.7780, 2275200]
        elif 1749601 < height <= 2023200:
            return [4.0, 0.1776, 3.8224, 2275200]
        elif 2023201 < height <= 2275200:
            return [2.0, 0.0888, 1.9112]


class V3tests:
    TESTERS_CHANNEL_ID = '1001679402521'
    TEST_CHANNEL_ID = '607280227'
    TEST_DEV_CHANNEL_ID = '803516752'
    TEAM_ICONS = {'bees': '🐝', 'rabbits': '🐇', 'owls': '🦉'}
    ADMIN_ID = '803516752'
