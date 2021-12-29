from mining_calculator import Rig
from parsers.mining import MiningParser

SEP = '-'


class MiningResponse:
    def __init__(self, user_query: MiningParser):
        self.complete = False
        self.user_query = user_query
        self.title = f"EPIC-RADAR: Mining Calculator"
        self.body = [self.title]
        self.lines = []
        self.init_lines()
        self.print = self.ready_msg()

    def _add_lines(self):
        for line in self.lines:
            self.body.append(f"{line}")

    def ready_msg(self):
        self._add_lines()
        return '\n'.join(self.body)

    def get_rig_report(self):
        algorithm = self.user_query.algo
        hashrate = self.user_query.hashrate

        if algorithm and hashrate:
            user_rig = Rig(hashrate=hashrate, algorithm=algorithm)
            return user_rig.get_report()

    def init_lines(self):
        if not self.user_query.algo:
            line = f'Provide mining algorithm'
            self.lines.append(line)
            print(line)
        if not self.user_query.hashrate:
            line = f'Provide your hardware hashrate'
            self.lines.append(line)
            print(line)

        data = self.get_rig_report()

        if data:
            self.complete = True
            hashrate = round(float(self.user_query.hashrate) / self.user_query.match_units_with_algo()[1], 1)
            currency = data['currency']
            reward = round(float(data['24h yield']), 2)
            income = round(float(data['currency_rig_profit']), 2)
            lines = [
                f"⚙ *{hashrate} {self.user_query.match_units_with_algo()[0]}* {self.user_query.get_algo().capitalize()}",
                f"◽ Solo block in: *{round(float(data['hours_for_block']), 2)}*h",
                ]
            self.title = f"⏱ 24h: *{reward} EPIC* | {income} {currency}"
            self.lines = lines

        else:
            self.complete = False
