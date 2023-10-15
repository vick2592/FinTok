import bitfinex
import datetime
import time
import pandas as pd
import os

def download_historical_data_to_csv(symbol, timeframe, limit, start_date, end_date):
    # Check if the CSV file exists and get the last datetime value
    csv_file_name = f"{symbol}_{timeframe}_historical.csv"
    last_datetime = None

    if os.path.exists(csv_file_name):
        existing_data = pd.read_csv(csv_file_name)
        if not existing_data.empty:
            last_datetime = existing_data['MTS'].iloc[-1]

    if last_datetime:
        start_date = last_datetime.timestamp() * 1000

    # Create api instance
    api_v2 = bitfinex.bitfinex_v2.api_v2()
    hour = 3600000  # 1 hour in milliseconds
    step = hour * limit
    data = []

    while start_date < end_date:
        if start_date + step > end_date:
            step = end_date - start_date

        end = start_date + step
        data += api_v2.candles(symbol=symbol, interval=timeframe, limit=limit, start=start_date, end=end)
        print(f"Downloaded data from {start_date} to {end}")
        start_date = end
        time.sleep(1.5)

    names = ['MTS', 'Open', 'Close', 'High', 'Low', 'Volume']
    df = pd.DataFrame(data, columns=names)
    df['MTS'] = pd.to_datetime(df['MTS'], unit='ms')
    df.set_index('MTS', inplace=True)
    df.sort_index(inplace=True)

    # Append new data to the existing CSV file or create a new one if it doesn't exist
    if os.path.exists(csv_file_name):
        existing_data = pd.read_csv(csv_file_name)
        updated_data = pd.concat([existing_data, df])
        updated_data.to_csv(csv_file_name, index=False)
    else:
        df.to_csv(csv_file_name, index=False)
