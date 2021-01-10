from datetime import date
from datetime import datetime

class Snapshot:
    def __init__(self, posts, items, trades):
        self.posts = posts
        self.items = items
        self.date = date.today().strftime("%d.%m.%Y") + datetime.now().strftime('_%H.%M.%S')
        self.trades = trades
