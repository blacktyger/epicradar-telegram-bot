from settings import Database, Vitex


class VitexParser:
    """Process Telegram User message, validate and return processed data"""
    DATABASE_API_URL = Database.API_URL
    VITEX_UPDATE_QUERY = API_GET_VITEX_UPDATE

    PATTERNS = Vitex.PATTERNS

    def __init__(self, message: str):
        self.message = message.split(' ')
        self.response = str
        self._parse_command()
        print(f"USER MESSAGE: {self.message}")

    def _parse_command(self):
        for cmd in self.message:
            if cmd in self.PATTERNS.keys():
                url = f"{self.DATABASE_API_URL}{self.API_GET_VITEX_UPDATE}"
                response = requests.get(url)
                self.response = response.json()
                print(self.response['price'])