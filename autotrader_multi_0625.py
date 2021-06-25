import logging

import pandas as pd
import datetime

from ibapi.contract import Contract
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.utils import iswrapper

# types
from ibapi.common import *  # @UnusedWildImport
from ibapi.order import Order
from ibapi.order_state import OrderState

from finta import TA
from collections import deque

futures_contract = Contract()
futures_contract.symbol = 'NQ'
futures_contract.secType = 'FUT'
futures_contract.exchange = 'GLOBEX'
futures_contract.currency = 'USD'
futures_contract.lastTradeDateOrContractMonth = "202109"

REQ_ID_TICK_BY_TICK_DATE = 1 # ID
NUM_PERIODS = 5 # length
ORDER_QUANTITY = 1 # number of contracts
ticks_per_candle = 8 # candle size
SHORT_TICKS_PER_CANDLE = 5
# initial_px = [14280, 14266.5, 14267.5, 14273.25, 14270.5, 14266.75, 14252.5, 14264.5, 14267.75] # manually obtain closing prices from TOS for n

initial_px = []

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
        self.short_ticks_per_candle = SHORT_TICKS_PER_CANDLE
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
        self.period_sum = self.periods * (self.periods + 1) // 2
        self.n = len(initial_px)
        # self.dq = deque()
        self.dq = deque(initial_px)
        self.wma = 0
        self.hma = 0
        self.signal = "NONE"
        self.high = 0
        self.max_value = 0
        self.min_value = 0
        self.atr_value = 0
        self.wma_target = 0
        self.target_up = 0
        self.target_down = 0
        self.dq1 = deque()
        self.dq2 = deque()
        self.i = 0
        self.j = 0
        self.prev_wma = 0
        self.prev_hma = 0
        self.prev_fast_wma = 0
        self.fast_wma = 0
        self.prev_fast_hma = 0
        self.fast_hma = 0

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

    def nextOrderId(self):
        oid = self.nextValidOrderId
        self.nextValidOrderId += 1
        return oid

    def tickDataOperations_req(self):
        self.reqTickByTickData(19002, futures_contract, "AllLast", 0, False)

    def shorter_candle(self, price: float):
        self.dq2.append(price)
        while len(self.dq2) > self.periods:
            self.dq2.popleft()

    def update_signal(self, price: float):
        self.dq.append(price) # populate deque with closing prices
        self.n += 1
        if self.n < self.periods: # checking the length of deque to make sure it is less than length of indicator
            return
        self.prev_wma = self.wma # to calculate slope i store the current value and call it previous value
        self.prev_hma = self.hma
        self.calc_wma() # new value - slope is new value - previous value

    def calc_wma(self):
        while len(self.dq) > self.periods:
            self.dq.popleft()
        data = list(self.dq) # convert deque to a list
        df = pd.DataFrame(data, columns=['close']) #put the list into a dataframe
        df['open'] = df['close']
        df['high'] = df['close']
        df['low'] = df['close']
        df['sma'] = TA.SMA(df, self.periods) # apply finta function for your favorite indicators
        self.wma = df['sma'].iloc[-1]
        df['hma'] = TA.SMA(df, 3)
        self.hma = df['hma'].iloc[-1]

    def update_fast_signal(self, price: float):
        self.dq2.append(price)
        self.j += 1
        if self.j < self.periods:
            return
        self.prev_fast_wma = self.fast_wma
        self.prev_fast_hma = self.fast_hma
        self.calc_fast_wma()

    def calc_fast_wma(self):
        while len(self.dq2) > self.periods:
            self.dq2.popleft()
        data_fast = list(self.dq2) # convert deque to a list
        df_fast = pd.DataFrame(data_fast, columns=['close']) #put the list into a dataframe
        df_fast['open'] = df_fast['close']
        df_fast['high'] = df_fast['close']
        df_fast['low'] = df_fast['close']
        df_fast['sma'] = TA.SMA(df_fast, self.periods) # apply finta function for your favorite indicators
        self.fast_wma = df_fast['sma'].iloc[-1]
        df_fast['hma'] = TA.SMA(df_fast, 3)
        self.fast_hma = df_fast['hma'].iloc[-1]


    # def calc_wma_clean(self):
    #     weight = 1
    #     wma_total = 0
    #     for price in self.dq:
    #         wma_total += price * weight
    #         weight += 1
    #     self.wma = wma_total / self.period_sum
    #     self.dq.popleft()

# this creates a signal - USE THIS
    def decision_engine(self):
        if self.prev_wma != 0:
            if self.prev_hma < self.prev_wma and self.hma > self.wma:
                self.signal = "LONG"
            elif self.prev_hma > self.prev_wma and self.hma < self.wma:
                self.signal = "SHORT"

        # if prev_wma != 0:
        #     if self.wma > prev_wma: # indicates moving to a positive slope
        #         self.signal = "LONG"
        #     elif self.wma < prev_wma: # indicates moving to a negative slope
        #         self.signal = "SHRT"

    # ignore this for now
    def update_target(self):
        if self.prev_wma != 0:
            if self.wma > self.prev_wma:
                diff = self.wma - self.prev_wma
                self.wma_target = self.wma + diff

            elif self.wma < self.prev_wma:
                diff = self.prev_wma - self.wma
                self.wma_target = self.wma - diff

    # ignore this for now

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

    # print the data
    def tickByTickAllLast(self, reqId: int, tickType: int, time: int, price: float,
                          size: int, tickAttribLast: TickAttribLast, exchange: str,
                          specialConditions: str):
        print(#"TickByTickAllLast. ",
              "Candle:", str(self.tick_count // self.ticks_per_candle + 1).zfill(3),
              "Tick:", str(self.tick_count % self.ticks_per_candle + 1).zfill(3),
              "Time:", datetime.datetime.fromtimestamp(time).strftime("%Y%m%d %H:%M:%S"),
              "Price:", "{:.2f}".format(price),
              #"Size:", size,
              #"Up Target", "{:.2f}".format(self.target_up), # ignore from here
              #"Down Target", "{:.2f}".format(self.target_down),
              "WMA:", "{:.2f}".format(self.wma),
              "HMA:", "{:.2f}".format(self.hma),
              "Fast_WMA:", "{:.2f}".format(self.fast_wma),
              "Fast_HMA:", "{:.2f}".format(self.fast_hma),
              #"WMA_Target", "{:.2f}".format(self.wma_target),
              # "High", self.strategy.max_value,
              # "Low", self.strategy.min_value,
              "ATR", self.atr_value,
              # "Tick_List:", self.strategy.dq1,
              "Current_List:", self.dq, # list of values for length of indicator
              "Fast List:", self.dq2,
              self.signal)
        if self.tick_count % self.ticks_per_candle == self.ticks_per_candle - 1:
            self.update_signal(price)
            self.update_fast_signal(price)
            self.decision_engine()
            self.checkAndSendOrder()
        if self.tick_count % self.short_ticks_per_candle == self.short_ticks_per_candle - 1:
            self.shorter_candle(price)
        self.find_high(price)
        self.tick_count += 1

# reporting order status

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

# reporting if there is open order

    @iswrapper
    def openOrder(self, orderId: OrderId, contract: Contract, order: Order,
                  orderState: OrderState):
        print("OpenOrder. ",
              "OrderId:", orderId,
              "Contract:", contract,
              "Order:", order,
              "OrderState:", orderState)

# here is where we send the trade

    def checkAndSendOrder(self):
        print(f"Received {self.signal}")
        print(f"Last signal {self.last_signal}")

        if self.signal == "NONE" or self.signal == self.last_signal: # here we don't keep adding trades w/ each candle
            print("Doing nothing")
            self.last_signal = self.signal
            return

        if self.signal == "LONG": # check the signal
            self.sendOrder("BUY") # fire trade or email yourself an alert
        elif self.signal == "SHORT" and self.last_signal != "NONE": # check signal
            self.sendOrder("SELL") # fire trade or email yourself an alert
        else:
            print("Don't want to go naked short")

        self.last_signal = self.signal

    def sendOrder(self, action): # defines the order object in the API
        order = Order()
        order.action = action
        order.totalQuantity = ORDER_QUANTITY
        order.orderType = "MKT"
        self.pending_order = True
        self.placeOrder(self.nextOrderId(), futures_contract, order)
        print(f"Sent a {order.action} order for {order.totalQuantity} shares")

def main():
    app = TestApp()
    try:
        # ! [connect]
        app.connect("127.0.0.1", port=7497, clientId=7) # make sure you have a different client id for each ticker
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