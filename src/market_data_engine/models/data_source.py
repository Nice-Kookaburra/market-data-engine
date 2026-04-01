class DataSource:
    def __init__(self, name, provider, api_key_ref, rate_limits):
        self.name = name                    # Primary Key
        self.provider = provider
        self.api_key_ref = api_key_ref
        self.rate_limits = rate_limits