import pandas as pd
from ibapi.utils import iswrapper
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
# types
from ibapi.common import *  # @UnusedWildImport
from ibapi.contract import * # @UnusedWildImport
from time import sleep
from datetime import datetime, timedelta

NUMBER_OF_ATTEMPTS = 100
START_DATE_FILENAME = 'start_date.txt'
RECORDING_FILENAME = 'tick_history_0813.csv'

class TestApp(EWrapper, EClient):
    def __init__(self):
        EWrapper.__init__(self)
        EClient.__init__(self, wrapper=self)
        self.data = []  # Initialize variable to store candle
        self.contract = Contract()
        self.now = datetime.now()
        self.current_time = self.now.strftime("%Y%m%d %H:%M:%S")
        self.first_time = 0

    def nextValidId(self, orderId: int):

        # we can start now
        self.start()

    def start(self):

        self.historicalTicksOperations()
        print("Executing requests ... finished")

    # https://interactivebrokers.github.io/tws-api/historical_time_and_sales.html

    def historicalTicksOperations(self):
        self.contract.symbol = 'NQ'
        self.contract.secType = 'FUT'
        self.contract.exchange = 'GLOBEX'
        self.contract.currency = 'USD'
        self.contract.lastTradeDateOrContractMonth = "202109"
        with open(START_DATE_FILENAME,
                  "r") as file1:
            passwd = file1.read()
        current_time = str(passwd)
        # current_time = passwd.strftime("%Y%m%d %H:%M:%S")
        self.reqHistoricalTicks(18002, self.contract,
                                " ", current_time, 1000, "TRADES", 0, True, []) # 1 is RTH and 0 is all hours
        # self.current_time = '20210731 09:39:33'
        # 20210731 09:39:33

    def historicalTicksLast(self, reqId: int, ticks: ListOfHistoricalTickLast,
                            done: bool):
        for tick in ticks:
            # print("HistoricalTickLast. ReqId:", reqId, tick)
            self.data.append([tick])
            #print(self.data)
            self.df = pd.DataFrame(self.data)               # convert list to a df
            self.df[0] = self.df.astype(str)                # convert df to a string
            self.df = self.df[0].str.split(expand=True)     # split the column by delimiters
            self.df = self.df[[1,8]]                        # select the time and price columns
            self.df.columns = ['time', 'price']             # name the columns
            self.df = self.df.replace(',','', regex=True)   # get rid of the commas
            self.df['time_converted'] = pd.to_datetime(self.df['time'], unit = 's') # convert to datetime
            self.df['time_converted'] = self.df['time_converted'] - timedelta(hours=4) # convert to EST

        self.first_time = self.df['time_converted'].iloc[0] # 0 for first value and -1 for last value

        self.first_time = self.first_time.strftime("%Y%m%d %H:%M:%S")

        print(self.first_time)
        with open(START_DATE_FILENAME, "w") as text_file:
            text_file.write(self.first_time)

        print(self.df)

        df1 = pd.read_csv(RECORDING_FILENAME, index_col=0) # https://stackoverflow.com/questions/20845213/how-to-avoid-python-pandas-creating-an-index-in-a-saved-csv
        print(df1)
        frames = [self.df, df1]
        result = pd.concat(frames, ignore_index=True)
        print(result)
        result.to_csv(RECORDING_FILENAME)  # https://stackoverflow.com/questions/20845213/how-to-avoid-python-pandas-creating-an-index-in-a-saved-csv

        self.disconnect()

def main():
    counter = 1
    end_time = datetime(2021, 7, 12, 18, 0, 1)
    with open(START_DATE_FILENAME,
              "r") as file1:
        passwd = file1.read()

    current = datetime.strptime(passwd, "%Y%m%d %H:%M:%S")
    while current > end_time:
        if counter % 59 != 0:
            print(f'Attempt:{counter}')
            app = TestApp()
            app.connect('127.0.0.1', 7497, 120)
            app.run()
            # sleep(0)
            current = app.df['time_converted'].iloc[-1]
            counter = counter + 1
        else:
            sleep(360)
            counter = counter + 1

if __name__ == "__main__":
    main()

