class IngestionJob:
    def __init__(self, job_id, symbols, start_date, end_date, status, run_time):
        self.job_id = job_id            # Primary Key
        self.symbols = symbols
        self.start_date = start_date
        self.end_date = end_date
        self.status = status
        self.run_time = run_time
        