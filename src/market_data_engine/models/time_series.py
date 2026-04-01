class TimeSeries:
    def __init__(self, asset, price_bars, frequency):
        self.asset = asset              # Asset object
        self.price_bars = price_bars    # This can either be an array / list or a dataframe wrapper of PriceBar
        self.frequency = frequency      # 1d, 1h, 1m, 1y etc
