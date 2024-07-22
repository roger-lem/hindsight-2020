import yfinance as yf
import yahooquery as yq
import pandas as pd
from datetime import datetime, timedelta


def get_all_us_tickers():
    screener = yq
    Screener()
    screen = screener.get_screeners('all_usa', count=10000)
    tickers = [item['symbol'] for item in screen['quotes']]
    return tickers


def get_stocks_data(tickers, start_date, end_date):
    data = {}
    for ticker in tickers:
        stock = yf.Ticker(ticker)
        data[ticker] = stock.history(start=start_date, end=end_date)
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
            if stock.info['marketCap'] and stock.info['marketCap'] >= min_market_cap:
                quadrupled_stocks.append(ticker)
    return quadrupled_stocks


def main():
    # Define parameters
    start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    end_date = datetime.now().strftime('%Y-%m-%d')
    min_market_cap = 1e10  # Minimum starting market cap (e.g., 10 billion)

    # Get all US tickers
    all_us_tickers = get_all_us_tickers()

    # Get stock data
    stock_data = get_stocks_data(all_us_tickers, start_date, end_date)

    # Find quadrupled stocks
    quadrupled_stocks = find_quadrupled_stocks(stock_data, min_market_cap)

    print("Stocks that quadrupled in value in the past year:")
    for stock in quadrupled_stocks:
        print(stock)


if __name__ == "__main__":
    main()
