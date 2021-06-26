import time
import random
from finta import TA
import pandas as pd
import yfinance as yf

# creates a stock simulator, generates an indicator and buy/sell signals
# can be ported to any market data API, for prices and FIX engine to send trades to the market

class StockSimulator:

    def __init__(self):
        self.counter = 0
        self.stock_price = 0
        self.stock_list = []
        self.indicator = 0
        self.signal = "NONE"
        self.yahoo_counter = 0
        self.df = pd.DataFrame()

    # This is the simulator that executes all the methods
    def simulator(self):
        num_candles_in_test_period = 10
        # length_of_indicator = 4
        sleep_seconds = 2
        self.generate_yahoo_stock_px()
        while self.counter < num_candles_in_test_period:
            self.choose_yahoo_stock_px()
            self.stock_list_mgr()
            self.update_signal()
            time.sleep(sleep_seconds)
            self.counter += 1

    # Generate the stock price
    def generate_stock_price(self):
        lowest_stock_px = 1
        highest_stock_px = 10
        self.stock_price = random.randint(lowest_stock_px, highest_stock_px)
        stock_px_formatted = "{:.2f}".format(self.stock_price)
        stock_price_msg = f'latest stock price: {stock_px_formatted}'
        print(stock_price_msg)

    def generate_yahoo_stock_px(self):
        ticker = "NQ=F"
        # data = yf.download(tickers=ticker, start='2010-01-04', end='2018-12-31')
        data = yf.download(tickers = ticker, period = "1mo")

        # valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
        # valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
        # https://pypi.org/project/yfinance/
        # data = yf.download("SPY AAPL", start="2017-01-01", end="2017-04-30")

        self.df = data
        self.df.to_csv('stock_px_sample.csv')

    def choose_yahoo_stock_px(self):
        self.stock_price = self.df['Close'].iloc[self.yahoo_counter]
        stock_px_formatted = "{:.2f}".format(self.stock_price)
        stock_price_msg = f'latest stock price: {stock_px_formatted}'
        print(stock_price_msg)
        self.yahoo_counter += 1

    # Create a list that collects most recent indicator length of stock prices
    def stock_list_mgr(self):
        length_of_indicator = 4
        self.stock_list.append(self.stock_price)
        if len(self.stock_list) > length_of_indicator:
            self.stock_list.pop(0)
        stock_list_msg = f'list of stock prices: {self.stock_list}'
        print(stock_list_msg)

    # Calculate indicator value by converting list to a dataframe and using Finta package
    def finta_indicator(self):
        df = pd.DataFrame()
        df['open'] = self.stock_list
        df['high'] = self.stock_list
        df['low'] = self.stock_list
        df['close'] = self. stock_list
        fin_ta_indicator = TA.WMA
        df['indicator'] = fin_ta_indicator(df, len(self.stock_list))
        recent_indicator_value = df['indicator'].iloc[-1]
        self.indicator = recent_indicator_value
        wma_formatted = "{:.2f}".format(self.indicator)
        fin_ta_formatted = fin_ta_indicator.__name__
        wma_msg = f'{fin_ta_formatted}: {wma_formatted}'
        print(wma_msg)

    # Generate buy/sell signal based on trend pointing up or down on indicator
    def update_signal(self):
        prev_indicator = self.indicator
        self.finta_indicator()
        if prev_indicator != 0:
            if self.indicator > prev_indicator:
                self.signal = "LONG at " + str(self.indicator) + ' or higher\n'
            elif self.indicator < prev_indicator:
                self.signal = "SHORT at " + str(self.indicator) + ' or lower\n'
        print(self.signal)

def main():
    app = StockSimulator()
    app.simulator()

if __name__ == "__main__":
    main()