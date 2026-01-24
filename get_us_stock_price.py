import time
from importlib.metadata import files
import yfinance as yf
from curl_cffi import requests
import pandas as pd

symbol_csv = "us_stock_symbol.csv"
output_prefix ="us_stock_pricing_part"
batch_100_sleep_time = 5
batch_1000_sleep_time = 30

session = requests.Session(impersonate="chrome")

symbol_df = pd.read_csv(symbol_csv)
symbols =  symbol_df["stock_symbol"].unique().tolist()
print(f"Total symbols: {len(symbols)}")

data_list = []
file_index = 1

for i,stock_symbol in enumerate(symbols,start=1):
    try:
        ticker = yf.Ticker(stock_symbol,session=session)
        df = ticker.history(period="10y")

        if df.empty:
            print(f"{stock_symbol} is empty")
            continue

        df = df.reset_index()
        df["symbol"] = stock_symbol
        df["Date"] = pd.to_datetime(df["Date"], utc=True)
        df["Date"] = df["Date"].dt.date
        df = df[["symbol", "Date", "Open", "High", "Low", "Close", "Volume"]]
        data_list.append(df)
        print(f"{i} {stock_symbol} OK")

    except Exception as e:
        print(f"{i} {stock_symbol} ERROR:{e}")

    if i % 1000 == 0:
        result_df = pd.concat(data_list,ignore_index=True)
        output_file = f"{output_prefix}_{file_index}.csv"
        result_df.to_csv(output_file, index=False, encoding="utf-8-sig")
        print(f"Saved {output_file}, rows={len(result_df)}")

        file_index += 1
        data_list = []

        print("time sleep 30 seconds")
        time.sleep(batch_1000_sleep_time)


    elif i % 100 == 0:
        print("time sleep 5 seconds")
        time.sleep(batch_100_sleep_time)



if data_list:
    result_df = pd.concat(data_list, ignore_index=True)
    output_file = f"{output_prefix}_{file_index}.csv"
    result_df.to_csv(output_file, index=False, encoding="utf-8-sig")
    print(f"Saved final {output_file}, rows={len(result_df)}")
