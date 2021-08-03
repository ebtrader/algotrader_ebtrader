import pandas as pd
from ibapi.utils import iswrapper
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
# types
from ibapi.common import *  # @UnusedWildImport
from ibapi.contract import * # @UnusedWildImport
from time import sleep
from datetime import datetime, timedelta

class TestApp(EWrapper, EClient):
    def __init__(self):
        EWrapper.__init__(self)
        EClient.__init__(self, wrapper=self)
        self.data = []  # Initialize variable to store candle
        self.contract = Contract()
        self.cols = ['data', 'open', 'high', 'low', 'close', 'volume']
        self.df = pd.DataFrame(columns=self.cols)
        self.now = datetime.now()
        self.current_time = self.now.strftime("%Y%m%d %H:%M:%S")
        self.nextValidOrderId = None
        self.first_time = 0

    def nextValidId(self, orderId: int):
        super().nextValidId(orderId)


        self.nextValidOrderId = orderId
        print("NextValidId:", orderId)
        # ! [nextvalidid]

        # we can start now
        self.start()

    def nextOrderId(self):
        oid = self.nextValidOrderId
        self.nextValidOrderId += 1
        return oid

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
        with open("sample_date.txt",
                  "r") as file1:
            passwd = file1.read()
        current_time = str(passwd)
        # current_time = passwd.strftime("%Y%m%d %H:%M:%S")
        self.reqHistoricalTicks(18002, self.contract,
                                " ", current_time, 1000, "TRADES", 1, True, []) # 1 is RTH and 0 is all hours
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

        self.first_time = self.df['time_converted'].iloc[0]

        self.first_time = self.first_time.strftime("%Y%m%d %H:%M:%S")

        print(self.first_time)
        with open("sample_date.txt", "w") as text_file:
            text_file.write(self.first_time)

        print(self.df)
        self.df.to_csv('tick_history_subset.csv')
        self.disconnect()


    # def historicalData(self, reqId: int, bar: BarData):
    #     #self.data.append([reqId, bar])
    #     self.df.loc[len(self.df)] = [bar.date, bar.open, bar.high, bar.low, bar.close, bar.volume]
    #     self.displ_hist()
    #     #print("HistoricalData. ReqId:", reqId, "BarData.", bar)
    #     #print(self.df)
    #     #self.df.to_csv('history1.csv')
    #
    # def displ_hist(self):
    #     # num_rows = len(self.df)
    #     if len(self.df) == 19:
    #         print(self.df)
    #         sleep(2)
    #         self.df.to_csv('history2.csv')
    #     self.disconnect()  # this is what allows the loop to keep going


def main():
    counter = 0
    while counter < 30:
        app = TestApp()
        app.connect('127.0.0.1', 7497, 121)
        app.run()
        sleep(3)
        counter = counter + 1

    # app = TestApp()
    # app.connect("127.0.0.1", port=7497, clientId=105)
    # print("serverVersion:%s connectionTime:%s" % (app.serverVersion(), app.twsConnectionTime()))
    # app.run()

if __name__ == "__main__":
    main()

