

class TickerMessageParser(MessageParser):
    def __init__(self, message, pattern):
        super().__init__(message, pattern)
        self.ticker = self.find_ticker()

    def find_ticker(self):
        if any(x in self.msg for x in self.pattern['price']):
            return 'price'

class TickerAnswer(Answer):
    def __init__(self, icon, title, message):
        super().__init__(icon, title)
        self.message = message
        self.parser = TickerMessageParser(self.message, patterns['ticker'])
        self.currency = 'USD'
        self.url = 'https://epicradar.tech/'
        self.r = self.read_response()
        self.init_lines()
        self.add_lines()
        self.print = self.ready_msg()

    def read_response(self):
        url = f"{self.url}api/data/"
        data = json.loads(requests.get(url).content)
        btc = data[0]
        usd = data[1]
        return {'BTC': btc, 'USD': usd}

    def init_lines(self):
        price = round(float(self.r[self.currency]['avg_price']), 2)
        btc_price = self.r['BTC']['avg_price']
        change_24h = self.r[self.currency]['percentage_change_24h']
        vol_24h_total = int((float(self.r[self.currency]['vol_24h']) + float(self.r['BTC']['vol_24h'])) / 10**3)

        lines = [
            f"💰 EPIC: *{price} {self.currency}* | *{btc_price} BTC*",
            f"📊 24H: *{change_24h} %* | Vol: *{vol_24h_total}k*",
            self.separator,
            f"🔎 More: *{self.url}*",
            ]

        self.lines = lines
        return lines
