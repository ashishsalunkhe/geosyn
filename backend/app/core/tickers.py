# Common NASDAQ/NYSE/OTC Tickers for Proactive Monitoring

# Top 100 by Market Cap (Sample)
MAJOR_TICKERS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA", "BRK-B", "JNJ", "V", 
    "UNH", "WMT", "JPM", "XOM", "PG", "MA", "AVGO", "HD", "ORCL", "CVX", 
    "LLY", "MRK", "ABBV", "PEP", "KO", "BAC", "COST", "PFE", "TMO", "CSCO", 
    "ABT", "DHR", "NKE", "ADBE", "LIN", "MCD", "DIS", "WFC", "PM", "UPS", 
    "TXN", "VZ", "MS", "NEE", "BMY", "RTX", "HON", "AMV", "CAT", "CPRT",
    "INTC", "IBM", "AMAT", "PLD", "SBUX", "GS", "ISRG", "DE", "MDLZ", "T",
    "BA", "GE", "LRCX", "GILD", "VRTX", "BKNG", "ADP", "MMC", "TJX", "ADI",
    "MDT", "SYK", "AMT", "PLTR", "EL", "C", "ZTS", "CI", "MO", "CB",
    "^GSPC", "CL=F", "GC=F", "^NSEI", "^BSESN"
]

# High Volatility / Social Chatter Triggers
OSINT_TARGET_TICKERS = [
    "GME", "AMC", "BB", "NKLA", "SPCE", "DWAC", "COIN", "MARA", "RIOT", "HOOD"
]

ALL_TRACKED_TICKERS = list(set(MAJOR_TICKERS + OSINT_TARGET_TICKERS))
