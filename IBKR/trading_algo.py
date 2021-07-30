import pandas as pd
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
# types
from ibapi.common import *  # @UnusedWildImport
from ibapi.contract import * # @UnusedWildImport
from ibapi.order import Order
from ibapi.order_state import OrderState
import datetime
from finta import TA

TICKS_PER_CANDLE = 50
MOVING_AVG_PERIOD_LENGTH = 3
MOVING_AVG_PERIOD_LENGTH_1 = 5
TICKS_PER_CANDLE_A = 60
MOVING_AVG_PERIOD_LENGTH_A = 3
MOVING_AVG_PERIOD_LENGTH_A1 = 5

class TestApp(EWrapper, EClient):
    def __init__(self):
        EWrapper.__init__(self)
        EClient.__init__(self, wrapper=self)
        self.nextValidOrderId = None
        self.permId2ord = {}
        self.contract = Contract()
        self.data = []
        self.data1 = []
        self.data_a = []
        self.data_a1 = []
        self.data_counter = 0
        self.data_counter1 = 0
        self.data_counter_a = 0
        self.data_counter_a1 = 0
        self.mov_avg_length = MOVING_AVG_PERIOD_LENGTH
        self.mov_avg_length1 = MOVING_AVG_PERIOD_LENGTH_1
        self.mov_avg_length_a = MOVING_AVG_PERIOD_LENGTH_A
        self.mov_avg_length_a1 = MOVING_AVG_PERIOD_LENGTH_A1
        self.ticks_per_candle = TICKS_PER_CANDLE
        self.ticks_per_candle_a = TICKS_PER_CANDLE_A
        self.tick_count = 0
        self.indicator = 0
        self.prev_indicator = 0
        self.indicator1 = 0
        self.prev_indicator1 = 0
        self.indicator_a = 0
        self.prev_indicator_a = 0
        self.indicator_a1 = 0
        self.prev_indicator_a1 = 0
        self.n = 0
        self.p = 0
        self.q = 0
        self.r = 0
        self.signal = 'NONE'
        self.prev_signal = 'NONE'

    def nextValidId(self, orderId: int):
        super().nextValidId(orderId)
        self.nextValidOrderId = orderId
        print("NextValidId:", orderId)

        # we can start now
        self.start()

    def nextOrderId(self):
        oid = self.nextValidOrderId
        self.nextValidOrderId += 1
        return oid

    def start(self):
        self.tickDataOperations_req()
        # self.accountOperations_req()
        print("Executing requests ... finished")

    def running_list(self, price: float):
        self.data.append(price)
        self.data_counter += 1
        if self.data_counter < self.mov_avg_length:
            return
        while len(self.data) > self.mov_avg_length:
            self.data.pop(0)

    def running_list1(self, price: float):
        self.data1.append(price)
        self.data_counter1 += 1
        if self.data_counter1 < self.mov_avg_length1:
            return
        while len(self.data1) > self.mov_avg_length1:
            self.data1.pop(0)

    def running_list_a(self, price: float):
        self.data_a.append(price)
        self.data_counter_a += 1
        if self.data_counter_a < self.mov_avg_length_a:
            return
        while len(self.data_a) > self.mov_avg_length_a:
            self.data_a.pop(0)

    def running_list_a1(self, price: float):
        self.data_a1.append(price)
        self.data_counter_a1 += 1
        if self.data_counter_a1 < self.mov_avg_length_a1:
            return
        while len(self.data_a1) > self.mov_avg_length_a1:
            self.data_a1.pop(0)

    def calc_indicator(self):
        df_indicator = pd.DataFrame(self.data, columns=['close'])
        df_indicator['open'] = df_indicator['close']
        df_indicator['high'] = df_indicator['close']
        df_indicator['low'] = df_indicator['close']
        df_indicator['indicator'] = TA.SMA(df_indicator, self.mov_avg_length) # choose indicator here
        self.indicator = df_indicator['indicator'].iloc[-1]

    def calc_prev_indicator(self):
        self.n += 1
        if self.n < self.mov_avg_length:
            return
        self.prev_indicator = self.indicator

    def calc_indicator1(self):
        df_indicator1 = pd.DataFrame(self.data1, columns=['close'])
        df_indicator1['open'] = df_indicator1['close']
        df_indicator1['high'] = df_indicator1['close']
        df_indicator1['low'] = df_indicator1['close']
        df_indicator1['indicator1'] = TA.SMA(df_indicator1, self.mov_avg_length1) # choose indicator here
        self.indicator1 = df_indicator1['indicator1'].iloc[-1]

    def calc_prev_indicator1(self):
        self.p += 1
        if self.p < self.mov_avg_length1:
            return
        self.prev_indicator1 = self.indicator1

    def calc_indicator_a(self):
        df_indicator_a = pd.DataFrame(self.data_a, columns=['close'])
        df_indicator_a['open'] = df_indicator_a['close']
        df_indicator_a['high'] = df_indicator_a['close']
        df_indicator_a['low'] = df_indicator_a['close']
        df_indicator_a['indicator_a'] = TA.SMA(df_indicator_a, self.mov_avg_length_a) # choose indicator here
        self.indicator_a = df_indicator_a['indicator_a'].iloc[-1]

    def calc_prev_indicator_a(self):
        self.q += 1
        if self.q < self.mov_avg_length_a:
            return
        self.prev_indicator_a = self.indicator_a

    def calc_indicator_a1(self):
        df_indicator_a1 = pd.DataFrame(self.data_a1, columns=['close'])
        df_indicator_a1['open'] = df_indicator_a1['close']
        df_indicator_a1['high'] = df_indicator_a1['close']
        df_indicator_a1['low'] = df_indicator_a1['close']
        df_indicator_a1['indicator_a1'] = TA.SMA(df_indicator_a1, self.mov_avg_length_a) # choose indicator here
        self.indicator_a1 = df_indicator_a1['indicator_a1'].iloc[-1]

    def calc_prev_indicator_a1(self):
        self.r += 1
        if self.r < self.mov_avg_length_a1:
            return
        self.prev_indicator_a1 = self.indicator_a1

    def decision_engine(self):
        if self.prev_indicator != 0:
            self.prev_signal = self.signal
            if self.prev_indicator < self.indicator and self.indicator > self.prev_indicator:
                self.signal = 'LONG'
            elif self.prev_indicator > self.indicator and self.indicator < self.prev_indicator:
                self.signal = 'SHORT'
            else:
                self.signal = self.prev_signal

    def create_order(self):
        if self.signal == self.prev_signal:
            print('Stay in position')
            return
        elif self.signal == 'LONG':
            self.send_order('BUY')
        elif self.signal == 'SHORT':
            self.send_order('SELL')
        else:
            print('Waiting for next order...')

    def send_order(self, action):
        order = Order()
        order.action = action
        order.totalQuantity = 1
        order.orderType = 'MKT'
        self.pending_order = True
        self.placeOrder(self.nextOrderId(), self.contract, order)
        print(f'Sent a {order.action} order')

    # run tick data
    def tickDataOperations_req(self):
        # Create contract object

        # futures contract
        self.contract.symbol = 'NQ'
        self.contract.secType = 'FUT'
        self.contract.exchange = 'GLOBEX'
        self.contract.currency = 'USD'
        self.contract.lastTradeDateOrContractMonth = "202109"

        # Request tick data
        self.reqTickByTickData(19002, self.contract, "AllLast", 0, False)

    # Receive tick data
    def tickByTickAllLast(self, reqId: int, tickType: int, time: int, price: float,
                          size: int, tickAttribLast: TickAttribLast, exchange: str,
                          specialConditions: str):
        print('Candle:', str(self.tick_count // self.ticks_per_candle+1).zfill(3),
              'Tick:', str(self.tick_count % self.ticks_per_candle + 1).zfill(3),
              'Candle_a:', str(self.tick_count // self.ticks_per_candle_a+1).zfill(3),
              'Tick_a:', str(self.tick_count % self.ticks_per_candle_a + 1).zfill(3),
              # 'Time:', datetime.datetime.fromtimestamp(time),
              "Price:", "{:.2f}".format(price),
              # 'Size:', size,
              'Indicator:', "{:.2f}".format(self.indicator),
              'Prev_Ind:', "{:.2f}".format(self.prev_indicator),
              'Ind1:', "{:.2f}".format(self.indicator1),
              'Prev_Ind1:', "{:.2f}".format(self.prev_indicator1),
              'Ind_a:', "{:.2f}".format(self.indicator_a),
              'Prev_Ind_a:', "{:.2f}".format(self.prev_indicator_a),
              'Ind_a1:', "{:.2f}".format(self.indicator_a1),
              'Prev_Ind_a1:', "{:.2f}".format(self.prev_indicator_a1),
              self.signal
        )
              # 'Data', self.data)
        if self.tick_count % self.ticks_per_candle == self.ticks_per_candle - 1:
            self.running_list(price)
            self.running_list1(price)
            self.calc_prev_indicator()
            self.calc_indicator()
            self.calc_prev_indicator1()
            self.calc_indicator1()
            self.decision_engine()
            self.create_order()

        if self.tick_count % self.ticks_per_candle_a == self.ticks_per_candle_a - 1:
            self.running_list_a(price)
            self.running_list_a1(price)
            self.calc_prev_indicator_a()
            self.calc_indicator_a()
            self.calc_prev_indicator_a1()
            self.calc_indicator_a1()

        self.tick_count += 1

def main():
    app = TestApp()
    app.connect("127.0.0.1", port=7497, clientId=101)
    print("serverVersion:%s connectionTime:%s" % (app.serverVersion(),app.twsConnectionTime()))
    app.run()

if __name__ == "__main__":
    main()