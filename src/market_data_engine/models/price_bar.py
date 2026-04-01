class PriceBar:
    def __init__(self, date, open, high, low, close, adj_close, volume):
        self.date = date
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.adj_close = adj_close
        self.volume = volume

        # Composite key: (asset_id, date, frequency)