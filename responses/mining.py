from mining_calculator import Rig
from parsers.mining import MiningParser


THUMBNAIL_URL = "https://i.ibb.co/c1V2H3J/tg-bot-mining-logo.png"
DEFAULT_TITLE = f"EPIC-RADAR: Mining Calculator"


class MiningResponse:
    def __init__(self, user_query: MiningParser):
        self.inline_response = ''
        self.chat_response = ''
        self.inline_title = DEFAULT_TITLE
        self.inline_lines = []
        self.chat_lines = []
        self.user_query = user_query
        self.thumb_url = THUMBNAIL_URL
        self.complete = False

    def get_rig_report(self):
        algorithm = self.user_query.algo
        hashrate = self.user_query.hashrate

        if algorithm and hashrate:
            user_rig = Rig(hashrate=hashrate, algorithm=algorithm)
            return user_rig.get_report()

    def prepare_lines(self):
        if not self.user_query.algo:
            line = f'Provide mining algorithm'
            self.inline_lines.append(line)
        if not self.user_query.hashrate:
            line = f'Provide your hardware hashrate'
            self.inline_lines.append(line)

        self.inline_response = '\n'.join(self.inline_lines)
        data = self.get_rig_report()

        if data:
            self.complete = True
            hashrate = round(float(self.user_query.hashrate) / self.user_query.match_units_with_algo()[1], 1)
            currency = data['currency']
            reward = round(float(data['24h yield']), 2)
            income = round(float(data['currency_rig_profit']), 2)

            # PREPARE INLINE RESPONSE (TITLE AND BODY, NO MARKDOWN)
            self.inline_title = f"⏱ 24h: {reward} EPIC | {income} {currency}"
            self.inline_lines = [
                f"⚙ {hashrate} {self.user_query.match_units_with_algo()[0]} {self.user_query.get_algo().capitalize()}",
                f"◽ Solo block in: {round(float(data['hours_for_block']), 2)}h",
                ]
            self.inline_response = '\n'.join(self.inline_lines)

            # PREPARE CHAT RESPONSE (ALL LINES, MARKDOWN ACCEPTED)
            self.chat_lines = '\n'.join([
                f"⏱ 24h: *{reward} EPIC* | *{income} {currency}*",
                f"⚙ *{hashrate} {self.user_query.match_units_with_algo()[0]}* {self.user_query.get_algo().capitalize()}",
                f"◽ Solo block in: *{round(float(data['hours_for_block']), 2)}h*",
                ])
            self.chat_response = '\n'.join(self.chat_lines)

        else:
            self.complete = False
