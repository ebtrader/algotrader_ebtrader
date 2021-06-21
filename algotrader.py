import mysql.connector
import csv
import argparse
import datetime

import collections
import inspect
import logging
import os.path
import time


import pandas as pd
import datetime
from ibapi import wrapper
from ibapi import utils
from ibapi.client import EClient
from ibapi.utils import iswrapper

from ibapi.contract import Contract


from ibapi.ticktype import TickType, TickTypeEnum
from ibapi import wrapper
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.utils import iswrapper
# types
from ibapi.common import *  # @UnusedWildImport
# from ibapi.order import *  # @UnusedWildImport

from ibapi.order import Order
from ibapi.order_state import OrderState
from ibapi.execution import Execution

from finta import TA
from collections import deque

eurusd_contract = Contract()
REQ_ID_TICK_BY_TICK_DATE = 1

NUM_PERIODS = 9
ORDER_QUANTITY = 1
ticks_per_candle = 144


def SetupLogger():
    if not os.path.exists("log"):
        os.makedirs("log")

    time.strftime("pyibapi.%Y%m%d_%H%M%S.log")

    recfmt = '(%(threadName)s) %(asctime)s.%(msecs)03d %(levelname)s %(filename)s:%(lineno)d %(message)s'

    timefmt = '%y%m%d_%H:%M:%S'

    # logging.basicConfig( level=logging.DEBUG,
    #                    format=recfmt, datefmt=timefmt)
    logging.basicConfig(filename=time.strftime("log/pyibapi.%y%m%d_%H%M%S.log"),
                        filemode="w",
                        level=logging.INFO,
                        format=recfmt, datefmt=timefmt)
    logger = logging.getLogger()
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    logger.addHandler(console)


def printWhenExecuting(fn):
    def fn2(self):
        print("   doing", fn.__name__)
        fn(self)
        print("   done w/", fn.__name__)

    return fn2

def printinstance(inst:Object):
    attrs = vars(inst)
    print(', '.join("%s: %s" % item for item in attrs.items()))

class Activity(Object):
    def __init__(self, reqMsgId, ansMsgId, ansEndMsgId, reqId):
        self.reqMsdId = reqMsgId
        self.ansMsgId = ansMsgId
        self.ansEndMsgId = ansEndMsgId
        self.reqId = reqId


class RequestMgr(Object):
    def __init__(self):
        # I will keep this simple even if slower for now: only one list of
        # requests finding will be done by linear search
        self.requests = []

    def addReq(self, req):
        self.requests.append(req)

    def receivedMsg(self, msg):
        pass

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
        #self.contract = contract
        self.ticks_per_candle = ticks_per_candle
        self.nextValidOrderId = None
        self.started = False
        self.done = False
        self.position = 0
        # self.strategy = strategies.WMA(NUM_PERIODS, ticks_per_candle)
        self.last_signal = "NONE"
        self.pending_order = False
        self.tick_count = 0
        self.periods = NUM_PERIODS
        self.ticks = ticks_per_candle
        self.n = 0
        self.dq = deque()
        self.wma = 0
        self.signal = "NONE"
        self.high = 0
        self.max_value = 0
        self.min_value = 0
        self.atr_value = 0
        self.wma_target = 0
        self.target_up = 0
        self.target_down = 0
        self.dq1 = deque()
        self.i = 0


    def dumpReqAnsErrSituation(self):
        logging.debug("%s\t%s\t%s\t%s" % ("ReqId", "#Req", "#Ans", "#Err"))
        for reqId in sorted(self.reqId2nReq.keys()):
            nReq = self.reqId2nReq.get(reqId, 0)
            nAns = self.reqId2nAns.get(reqId, 0)
            nErr = self.reqId2nErr.get(reqId, 0)
            logging.debug("%d\t%d\t%s\t%d" % (reqId, nReq, nAns, nErr))

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
            self.tickDataOperations_req()

            print("Executing requests ... finished")

    def keyboardInterrupt(self):
        self.nKeybInt += 1
        if self.nKeybInt == 1:
            self.stop()
        else:
            print("Finishing test")
            self.done = True

    def stop(self):
        print("Executing cancels")
        # self.orderOperations_cancel()
        # self.accountOperations_cancel()
        # self.tickDataOperations_cancel()
        self.marketDepthOperations_cancel()
        # self.realTimeBarsOperations_cancel()
        # self.historicalDataOperations_cancel()
        # self.optionsOperations_cancel()
        # self.marketScanners_cancel()
        # self.fundamentalsOperations_cancel()
        # self.bulletinsOperations_cancel()
        # self.newsOperations_cancel()
        # self.pnlOperations_cancel()
        # self.histogramOperations_cancel()
        # self.continuousFuturesOperations_cancel()
        # self.tickByTickOperations_cancel()
        print("Executing cancels ... finished")

    def nextOrderId(self):
        oid = self.nextValidOrderId
        self.nextValidOrderId += 1
        return oid

    @iswrapper
    # ! [error]
    def error(self, reqId: TickerId, errorCode: int, errorString: str):
        super().error(reqId, errorCode, errorString)
        print("Error. Id:", reqId, "Code:", errorCode, "Msg:", errorString)
        errormsg = "IB error id %d errorcode %d string %s" % (reqId, errorCode, errorString)
        self._my_errors = errormsg

    @iswrapper
    def winError(self, text: str, lastError: int):
        super().winError(text, lastError)



    @printWhenExecuting
    def tickDataOperations_req(self):
        # Create contract object

        eurusd_contract.symbol = 'NQ'
        eurusd_contract.secType = 'FUT'
        eurusd_contract.exchange = 'GLOBEX'
        eurusd_contract.currency = 'USD'
        eurusd_contract.lastTradeDateOrContractMonth = "202109"

        self.reqTickByTickData(19002, eurusd_contract, "AllLast", 0, False)


    def historicalData(self, reqId:int, bar: BarData):
        print("HistoricalData. ReqId:", reqId, "BarData.", bar)
        logging.debug("ReqId:", reqId, "BarData.", bar)


    @iswrapper
    def tickPrice(self, tickerId: TickerId , tickType: TickType, price: float, attrib):
        super().tickPrice(tickerId, tickType, price, attrib)
        print("Tick Price, Ticker Id:", tickerId, "tickType:", TickTypeEnum.to_str(tickType), "Price:", price, " Time:", attrib.time, file=sys.stderr, end= " ")

    @iswrapper
    def tickSize(self, tickerId: TickerId, tickType: TickType, size: int):
        super().tickSize(tickerId, tickType, size)
        print( "Tick Size, Ticker Id:",tickerId,  "tickType:", TickTypeEnum.to_str(tickType),  "Size:", size, file=sys.stderr)

    def calc_wma(self):
        data = list(self.dq)
        df = pd.DataFrame(data, columns=['close'])
        df['open'] = df['close']
        df['high'] = df['close']
        df['low'] = df['close']
        df['sma'] = TA.WMA(df, self.periods)
        self.wma = df['sma'].iloc[-1]
        self.dq.popleft()

    def update_signal(self, price: float):
        self.dq.append(price)
        self.n += 1
        if self.n < self.periods:
            return
        prev_wma = self.wma
        self.calc_wma()

        if prev_wma != 0:
            if self.wma > prev_wma:
                diff = self.wma - prev_wma
                self.wma_target = self.wma + diff

            elif self.wma < prev_wma:
                diff = prev_wma - self.wma
                self.wma_target = self.wma - diff

        if prev_wma != 0:
            if self.wma > prev_wma:
                self.signal = "LONG"
            elif self.wma < prev_wma:
                self.signal = "SHRT"

    def find_high(self, price: float):
        multiplier = 0.5
        self.dq1.append(price)
        self.max_value = max(self.dq1)
        self.min_value = min(self.dq1)
        self.atr_value = self.max_value - self.min_value
        self.target_up = self.wma_target + self.atr_value * multiplier
        self.target_down = self.wma_target - self.atr_value * multiplier
        self.i += 1
        if self.i > self.ticks:
            self.dq1.popleft()


    def tickByTickAllLast(self, reqId: int, tickType: int, time: int, price: float,
                          size: int, tickAttribLast: TickAttribLast, exchange: str,
                          specialConditions: str):
        print("TickByTickAllLast. ",
              "Candle:", str(self.tick_count // self.ticks_per_candle + 1).zfill(3),
              "Tick:", str(self.tick_count % self.ticks_per_candle + 1).zfill(3),
              "Time:", datetime.datetime.fromtimestamp(time).strftime("%Y%m%d %H:%M:%S"),
              "Price:", "{:.2f}".format(price),
              "Size:", size,
              "Up Target", "{:.2f}".format(self.target_up),
              "Down Target", "{:.2f}".format(self.target_down),
              "WMA:", "{:.2f}".format(self.wma),
              "WMA_Target", "{:.2f}".format(self.wma_target),
              # "High", self.strategy.max_value,
              # "Low", self.strategy.min_value,
              "ATR", self.atr_value,
              self.signal)
              # "Tick_List:", self.strategy.dq1,
              # "Current_List:", self.strategy.dq)
        if self.tick_count % self.ticks_per_candle == self.ticks_per_candle - 1:
            self.update_signal(price)
            self.checkAndSendOrder()
        self.find_high(price)
        self.tick_count += 1

    @iswrapper
    def orderStatus(self, orderId: OrderId, status: str, filled: float,
                    remaining: float, avgFillPrice: float, permId: int,
                    parentId: int, lastFillPrice: float, clientId: int,
                    whyHeld: str, mktCapPrice: float):
        print("OrderStatus. ",
              "OrderId:", orderId,
              "Status:", status,
              "Filled:", filled,
              "Remaining:", remaining,
              "AvgFillPrice:", avgFillPrice,
              "PermId:", permId,
              "ParentId:", parentId,
              "LastFillPrice:", lastFillPrice,
              "ClientId:", clientId,
              "WhyHeld:", whyHeld,
              "MktCapPrice:", mktCapPrice)

    @iswrapper
    def openOrder(self, orderId: OrderId, contract: Contract, order: Order,
                  orderState: OrderState):
        print("OpenOrder. ",
              "OrderId:", orderId,
              "Contract:", contract,
              "Order:", order,
              "OrderState:", orderState)

    def checkAndSendOrder(self):
        print(f"Received {self.signal}")
        print(f"Last signal {self.last_signal}")

        if self.signal == "NONE" or self.signal == self.last_signal:
            print("Doing nothing")
            self.last_signal = self.signal
            return

        if self.signal == "LONG":
            self.sendOrder("BUY")
        elif self.signal == "SHRT" and self.last_signal != "NONE":
            self.sendOrder("SELL")
        else:
            print("Don't want to go naked short")

        self.last_signal = self.signal

    def sendOrder(self, action):
        order = Order()
        order.action = action
        order.totalQuantity = ORDER_QUANTITY
        order.orderType = "MKT"
        self.pending_order = True
        self.placeOrder(self.nextOrderId(), eurusd_contract, order)
        print(f"Sent a {order.action} order for {order.totalQuantity} shares")

def main():
    SetupLogger()
    logging.getLogger().setLevel(logging.ERROR)

    cmdLineParser = argparse.ArgumentParser("api tests")
    # cmdLineParser.add_option("-c", action="store_True", dest="use_cache", default = False, help = "use the cache")
    # cmdLineParser.add_option("-f", action="store", type="string", dest="file", default="", help="the input file")
    cmdLineParser.add_argument("-p", "--port", action="store", type=int,
                               dest="port", default=7497, help="The TCP port to use")
    cmdLineParser.add_argument("-C", "--global-cancel", action="store_true",
                               dest="global_cancel", default=False,
                               help="whether to trigger a globalCancel req")
    args = cmdLineParser.parse_args()
    print("Using args", args)
    logging.debug("Using args %s", args)
    # print(args)

    # tc = TestClient(None)
    # tc.reqMktData(1101, ContractSamples.USStockAtSmart(), "", False, None)
    # print(tc.reqId2nReq)
    # sys.exit(1)
    app = TestApp()
    try:
        if args.global_cancel:
            app.globalCancelOnly = True
        # ! [connect]
        app.connect("127.0.0.1", args.port, clientId=7)
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