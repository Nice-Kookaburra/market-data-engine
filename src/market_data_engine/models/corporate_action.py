class CorporateAction:
    def __init__(self, asset_id, type, date, value):
        self.asset_id = asset_id
        self.type = type    # Split or Dividend
        self.date = date
        self.value = value