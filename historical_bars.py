import logging

import pandas as pd
import datetime

from ibapi.contract import Contract
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.utils import iswrapper

# types
from ibapi.common import *  # @UnusedWildImport


futures_contract = Contract()
futures_contract.symbol = 'NQ'
futures_contract.secType = 'FUT'
futures_contract.exchange = 'GLOBEX'
futures_contract.currency = 'USD'
futures_contract.lastTradeDateOrContractMonth = "202109"

# ! [socket_init]
class TestApp(EWrapper, EClient):
    def __init__(self):
        EWrapper.__init__(self)
        EClient.__init__(self, wrapper=self)
        # ! [socket_init]
        self.nKeybInt = 0
        self.started = False
        self.nextValidOrderId = None
        self.permId2ord = {}
        self.globalCancelOnly = False
        self.simplePlaceOid = None
        self._my_errors = {}
        self.cols = ['date', 'open', 'high', 'low', 'close', 'volume']
        self.df = pd.DataFrame(columns=self.cols)

    @iswrapper
    # ! [connectack]
    def connectAck(self):
        if self.asynchronous:
            self.startApi()

    # ! [connectack]

    @iswrapper
    # ! [nextvalidid]
    def nextValidId(self, orderId: int):
        super().nextValidId(orderId)

        logging.debug("setting nextValidOrderId: %d", orderId)
        self.nextValidOrderId = orderId
        print("NextValidId:", orderId)
        # ! [nextvalidid]

        # we can start now
        self.start()

    def start(self):
        if self.started:
            return

        self.started = True

        if self.globalCancelOnly:
            print("Executing GlobalCancel only")
            self.reqGlobalCancel()
        else:
            print("Executing requests")
            self.historicalDataOperations_req()

            print("Executing requests ... finished")

    def nextOrderId(self):
        oid = self.nextValidOrderId
        self.nextValidOrderId += 1
        return oid

    def tickDataOperations_req(self):
        self.reqTickByTickData(19002, futures_contract, "AllLast", 0, False)

    # print the data
    def historicalDataOperations_req(self):
        queryTime = (datetime.datetime.today() - datetime.timedelta(days=1)).strftime("%Y%m%d %H:%M:%S")
        self.reqHistoricalData(4102, futures_contract, queryTime,
                               "2000 S", "5 secs", "TRADES", 1, 1, False, [])

    # ! [historicaldata]
    def historicalData(self, reqId:int, bar: BarData):
        # print("HistoricalData. ReqId:", reqId, "BarData.", bar)
        self.df.loc[len(self.df)] = [bar.date, bar.open, bar.high, bar.low, bar.close, bar.volume]
        self.df.to_csv('history2.csv')
        # print(self.df)
        self.disconnect()
    # ! [historicaldata]


def main():
    app = TestApp()
    try:
        # ! [connect]
        app.connect("127.0.0.1", port=7497, clientId=8) # make sure you have a different client id for each ticker
        # ! [connect]
        print("serverVersion:%s connectionTime:%s" % (app.serverVersion(),
                                                      app.twsConnectionTime()))
        # ! [clientrun]
        app.run()

        # ! [clientrun]
    except:
        raise

if __name__ == "__main__":
    main()