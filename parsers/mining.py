import re

from settings import Database, Mining

DJANGO_API_URL = Database.API_URL


class MiningParser:
    """Process Telegram User message, validate and return processed data"""

    algo_patterns = Mining.PATTERNS['mining_algorithms']
    unit_patterns = Mining.PATTERNS['units']

    def __init__(self, message: str):
        self.message = message.split(' ')

        self.unit = None
        self.algo = self.get_algo()
        self.hashrate = self.get_hashrate()

        print(f"USER MESSAGE: {self.message}")

    def get_algo(self):
        """Find what kind of algorithm is given by user and return it"""
        algo = None
        if any(x in self.message for x in self.algo_patterns['progpow']):
            algo = 'progpow'
        if any(x in self.message for x in self.algo_patterns['randomx']):
            algo = 'randomx'
        if any(x in self.message for x in self.algo_patterns['cuckoo']):
            algo = 'cuckoo'
        return algo

    def _units(self, source=None):
        """Find what kind of unit is used by user and return it"""
        if not source:
            source = self.message

        for unit in self.unit_patterns:
            for key in self.unit_patterns[unit]:
                for match in source:
                    if key in match:
                        self.unit = unit
                        print(self.unit)
        return self.unit

    def get_units(self):
        if self.unit == "kilohash":
            return 'KH/s', 10 ** 3
        elif self.unit == "megahash":
            return 'MH/s', 10 ** 6
        elif self.unit == "gigahash":
            return 'GH/s', 10 ** 9
        else:
            return 'H/s', 1

    def get_hashrate(self):
        """Find rig hashrate given by user and return it"""
        pat = re.compile(r"\d*\.?\d+|[-+]?\d+")
        temp_hashrate = list(filter(pat.match, self.message))

        if temp_hashrate:
            value = float(re.search(r"\d*\.?\d+|[-+]?\d+", temp_hashrate[0]).group())

            self._units()
            if not self.unit:
                temp_unit = [temp_hashrate[0].split('value')]
                self._units(temp_unit)

                if self.unit:
                    print(f'Unit found without space, {self.unit}')
                else:
                    self.unit = 'hash'
                    print('No unit found in message, using H/s')

            hashrate = value * self.get_units()[1]
            print(f"PARSED HASHRATE: {value} UNIT: {self.unit} ({hashrate} H/s)")
            return hashrate
        else:
            print(f'No hashrate found in {self.message}')

    def match_units_with_algo(self):
        if self.algo == "cuckoo":
            return 'GH/s', 10 ** 9
        if self.algo == "progpow":
            return 'MH/s', 10 ** 6
        if self.algo == 'randomx':
            return 'KH/s', 10 ** 3

