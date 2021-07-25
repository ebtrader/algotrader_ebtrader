import pandas as pd
from ibapi.utils import iswrapper
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
# types
from ibapi.common import *  # @UnusedWildImport
from ibapi.contract import * # @UnusedWildImport

class TestApp(EWrapper, EClient):
    def __init__(self):
        EWrapper.__init__(self)
        EClient.__init__(self, wrapper=self)
        self.data = []  # Initialize variable to store candle
        self.contract = Contract()

    def nextValidId(self, orderId: int):
        # we can start now
        self.start()

    def start(self):
        self.historicalDataOperations_req()
        print("Executing requests ... finished")

    def historicalDataOperations_req(self):
        self.contract.symbol = "TQQQ"
        self.contract.secType = "OPT"
        self.contract.exchange = "SMART"
        self.contract.currency = "USD"
        self.contract.lastTradeDateOrContractMonth = "20210730"
        self.contract.strike = 128
        self.contract.right = "C"
        self.contract.multiplier = "100"

        self.reqHistoricalData(4103, self.contract, '',
                               "2 D", "1 hour", "MIDPOINT", 1, 1, False, [])


    def historicalData(self, reqId: int, bar: BarData):
        self.data.append([reqId, bar])
        #print("HistoricalData. ReqId:", reqId, "BarData.", bar)

        df = pd.DataFrame(self.data)
        if len(df) == 14: # start analysis after the loop is complete
            print(df)
        df.to_csv('history.csv')
        self.disconnect()

def main():
    app = TestApp()
    app.connect("127.0.0.1", port=7497, clientId=102)
    print("serverVersion:%s connectionTime:%s" % (app.serverVersion(), app.twsConnectionTime()))
    app.run()


if __name__ == "__main__":
    main()

