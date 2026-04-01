class Asset:
    def __init__(self, asset_id, ticker, exchange, name, currency, asset_type):
        self.asset_id = asset_id        # Primary Key
        self.ticker = ticker            # Like GOOG, NVDA, etc
        self.exchange = exchange        # Where it trades
        self.name = name
        self.currency = currency
        self.asset_type = asset_type    # stock, etf, crypto, etc
