import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from yahooquery import Ticker


# Get list of tickers from Nasdaq and NYSE
def get_us_tickers():
    nasdaq_url = 'ftp://ftp.nasdaqtrader.com/SymbolDirectory/nasdaqlisted.txt'
    nyse_url = 'ftp://ftp.nasdaqtrader.com/SymbolDirectory/otherlisted.txt'
    nasdaq_tickers = pd.read_csv(nasdaq_url, sep='|')['Symbol'].tolist()
    nyse_tickers = pd.read_csv(nyse_url, sep='|')['ACT Symbol'].tolist()
    return nasdaq_tickers + nyse_tickers


# Function to filter out non-standard tickers and non-companies
def filter_tickers(tickers):
    filtered_tickers = []
    for ticker in tickers:
        if isinstance(ticker, str) and len(ticker) <= 4 and ticker.isalpha():
            try:
                info = Ticker(ticker).summary_profile[ticker]
                if info and info.get('industry'):  # Check if it has an industry, indicating it's a company
                    filtered_tickers.append(ticker)
            except Exception as e:
                print(f"Error fetching profile for {ticker}: {e}")
    return filtered_tickers


# Fetch stock data in batches to avoid rate limits
def get_stocks_data(tickers, start_date, end_date):
    data = {}
    batch_size = 200  # Adjust the batch size if necessary
    for i in range(0, len(tickers), batch_size):
        batch = tickers[i:i + batch_size]
        for ticker in batch:
            try:
                stock = yf.Ticker(ticker)
                stock_data = stock.history(start=start_date, end=end_date)
                if not stock_data.empty:
                    data[ticker] = stock_data
            except Exception as e:
                print(f"Error fetching data for {ticker}: {e}")
                # Retry with a different period if the initial period is invalid
                try:
                    stock_data = stock.history(period='max')
                    if not stock_data.empty:
                        data[ticker] = stock_data
                except Exception as retry_e:
                    print(f"Retry error fetching data for {ticker}: {retry_e}")
    return data


def find_quadrupled_stocks(data, min_market_cap):
    quadrupled_stocks = []
    for ticker, df in data.items():
        if df.empty:
            continue
        df['Max Price'] = df['Close'].rolling(window=365, min_periods=1).max()
        df['Quadrupled'] = df['Close'] >= 4 * df['Max Price'].shift(365)
        if df['Quadrupled'].any():
            stock = yf.Ticker(ticker)
            try:
                if stock.info['marketCap'] and stock.info['marketCap'] >= min_market_cap:
                    quadrupled_stocks.append(ticker)
            except Exception as e:
                print(f"Error fetching market cap for {ticker}: {e}")
    return quadrupled_stocks


def main():
      for x in range(x):
        # Define parameters
        start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        end_date = datetime.now().strftime('%Y-%m-%d')
        min_market_cap = 1e8  # Minimum starting market cap (e.g., 10 billion)

        # Get US tickers
        all_us_tickers = get_us_tickers()
        filtered_tickers = filter_tickers(all_us_tickers)

        # Get stock data
        stock_data = get_stocks_data(filtered_tickers, start_date, end_date)

        # Find quadrupled stocks
        quadrupled_stocks = find_quadrupled_stocks(stock_data, min_market_cap)

        print("Stocks that quadrupled in value in the past year:")
        for stock in quadrupled_stocks:
            print(stock)


if __name__ == "__main__":
    main()
