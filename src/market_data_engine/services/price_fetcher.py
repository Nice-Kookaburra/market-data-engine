import yfinance as yf

# Fetches data given an interval and period
def fetchHistoricData(index, interval, period, ticker):
    tick = yf.Ticker(ticker)
    return

# Fetches data from the earliest to the latest dates given
# 1/1/2001 - 1/1/2020
def fetchHistoricalDataWithinTwoPeriods(index, date_start, date_end, ticker):
    tick = yf.Ticker(ticker)
    hist = tick.history(
        start=date_start,
        end=date_end
    )

    
    return

