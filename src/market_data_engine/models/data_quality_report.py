class DataQualityReport:
    def __init__(self, asset_id, missingness, outliers, stale_flags):
        self.asset_id = asset_id
        self.missingness = missingness
        self.outliers = outliers
        self.stale_flags = stale_flags