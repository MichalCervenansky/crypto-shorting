import pandas as pd
from datetime import datetime

if __name__ == '__main__':
    filename = "btcusd.csv"
    df = pd.read_csv(filename, parse_dates=True)
    df["Time"] = df.Time.map(lambda x: datetime.fromtimestamp(x / 1000).strftime('%Y-%m-%d %H:%M:%S'))
    df.to_csv(filename, index=False)
