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

TICKS_PER_CANDLE_TF1 = 144
MOVING_AVG_PERIOD_LENGTH_TF1_S = 14 # slow timeframe (indicator)
MOVING_AVG_PERIOD_LENGTH_TF1_F = 9 # fast timeframe (indicator1)
TICKS_PER_CANDLE_TF2 = 89
MOVING_AVG_PERIOD_LENGTH_TF2_S = 14
MOVING_AVG_PERIOD_LENGTH_TF2_F = 9

class TestApp(EWrapper, EClient):
    def __init__(self):
        EWrapper.__init__(self)
        EClient.__init__(self, wrapper=self)
        self.nextValidOrderId = None
        self.permId2ord = {}
        self.contract = Contract()
        self.data_tf1_s = []
        self.data_tf1_f = []
        self.data_tf2_s = []
        self.data_tf2_f = []
        self.data_counter_tf1_s = 0
        self.data_counter_tf1_f = 0
        self.data_counter_tf2_s = 0
        self.data_counter_tf2_f = 0
        self.mov_avg_length_tf1_s = MOVING_AVG_PERIOD_LENGTH_TF1_S
        self.mov_avg_length_tf1_f = MOVING_AVG_PERIOD_LENGTH_TF1_F
        self.mov_avg_length_tf2_s = MOVING_AVG_PERIOD_LENGTH_TF2_S
        self.mov_avg_length_tf2_f = MOVING_AVG_PERIOD_LENGTH_TF2_F
        self.ticks_per_candle_tf1 = TICKS_PER_CANDLE_TF1
        self.ticks_per_candle_tf2 = TICKS_PER_CANDLE_TF2
        self.tick_count = 0
        self.indicator_tf1_s = 0
        self.prev_indicator_tf1_s = 0
        self.indicator_tf1_f = 0
        self.prev_indicator_tf1_f = 0
        self.indicator_tf2_s = 0
        self.prev_indicator_tf2_s = 0
        self.indicator_tf2_f = 0
        self.prev_indicator_tf2_f = 0
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

    def running_list_tf1_s(self, price: float):
        self.data_tf1_s.append(price)
        self.data_counter_tf1_s += 1
        if self.data_counter_tf1_s < self.mov_avg_length_tf1_s:
            return
        while len(self.data_tf1_s) > self.mov_avg_length_tf1_s:
            self.data_tf1_s.pop(0)

    def running_list_tf1_f(self, price: float):
        self.data_tf1_f.append(price)
        self.data_counter_tf1_f += 1
        if self.data_counter_tf1_f < self.mov_avg_length_tf1_f:
            return
        while len(self.data_tf1_f) > self.mov_avg_length_tf1_f:
            self.data_tf1_f.pop(0)

    def running_list_tf2_s(self, price: float):
        self.data_tf2_s.append(price)
        self.data_counter_tf2_s += 1
        if self.data_counter_tf2_s < self.mov_avg_length_tf2_s:
            return
        while len(self.data_tf2_s) > self.mov_avg_length_tf2_s:
            self.data_tf2_s.pop(0)

    def running_list_tf2_f(self, price: float):
        self.data_tf2_f.append(price)
        self.data_counter_tf2_f += 1
        if self.data_counter_tf2_f < self.mov_avg_length_tf2_f:
            return
        while len(self.data_tf2_f) > self.mov_avg_length_tf2_f:
            self.data_tf2_f.pop(0)

    def calc_indicator_tf1_s(self):
        df_indicator_tf1_s = pd.DataFrame(self.data_tf1_s, columns=['close'])
        df_indicator_tf1_s['open'] = df_indicator_tf1_s['close']
        df_indicator_tf1_s['high'] = df_indicator_tf1_s['close']
        df_indicator_tf1_s['low'] = df_indicator_tf1_s['close']
        df_indicator_tf1_s['indicator'] = TA.SMA(df_indicator_tf1_s, self.mov_avg_length_tf1_s) # choose indicator here
        self.indicator_tf1_s = df_indicator_tf1_s['indicator'].iloc[-1]

    def calc_prev_indicator_tf1_s(self):
        self.n += 1
        if self.n < self.mov_avg_length_tf1_s:
            return
        self.prev_indicator_tf1_s = self.indicator_tf1_s

    def calc_indicator_tf1_f(self):
        df_indicator_tf1_f = pd.DataFrame(self.data_tf1_f, columns=['close'])
        df_indicator_tf1_f['open'] = df_indicator_tf1_f['close']
        df_indicator_tf1_f['high'] = df_indicator_tf1_f['close']
        df_indicator_tf1_f['low'] = df_indicator_tf1_f['close']
        df_indicator_tf1_f['indicator1'] = TA.SMA(df_indicator_tf1_f, self.mov_avg_length_tf1_f) # choose indicator here
        self.indicator_tf1_f = df_indicator_tf1_f['indicator1'].iloc[-1]

    def calc_prev_indicator_tf1_f(self):
        self.p += 1
        if self.p < self.mov_avg_length_tf1_f:
            return
        self.prev_indicator_tf1_f = self.indicator_tf1_f

    def calc_indicator_tf2_s(self):
        df_indicator_tf2_s = pd.DataFrame(self.data_tf2_s, columns=['close'])
        df_indicator_tf2_s['open'] = df_indicator_tf2_s['close']
        df_indicator_tf2_s['high'] = df_indicator_tf2_s['close']
        df_indicator_tf2_s['low'] = df_indicator_tf2_s['close']
        df_indicator_tf2_s['indicator_a'] = TA.SMA(df_indicator_tf2_s, self.mov_avg_length_tf2_s) # choose indicator here
        self.indicator_tf2_s = df_indicator_tf2_s['indicator_a'].iloc[-1]

    def calc_prev_indicator_tf2_s(self):
        self.q += 1
        if self.q < self.mov_avg_length_tf2_s:
            return
        self.prev_indicator_tf2_s = self.indicator_tf2_s

    def calc_indicator_tf2_f(self):
        df_indicator_tf2_f = pd.DataFrame(self.data_tf2_f, columns=['close'])
        df_indicator_tf2_f['open'] = df_indicator_tf2_f['close']
        df_indicator_tf2_f['high'] = df_indicator_tf2_f['close']
        df_indicator_tf2_f['low'] = df_indicator_tf2_f['close']
        df_indicator_tf2_f['indicator_a1'] = TA.SMA(df_indicator_tf2_f, self.mov_avg_length_tf2_f) # choose indicator here
        self.indicator_tf2_f = df_indicator_tf2_f['indicator_a1'].iloc[-1]

    def calc_prev_indicator_tf2_f(self):
        self.r += 1
        if self.r < self.mov_avg_length_tf2_f:
            return
        self.prev_indicator_tf2_f = self.indicator_tf2_f

    def decision_engine(self):
        if self.prev_indicator_tf1_s != 0:
            self.prev_signal = self.signal
            if self.prev_indicator_tf1_s < self.indicator_tf1_s:
                self.signal = 'LONG'
            elif self.prev_indicator_tf1_s > self.indicator_tf1_s:
                self.signal = 'SHORT'
            else:
                self.signal = self.prev_signal

    def decision_engine_crossover(self):
        if self.prev_indicator_tf1_s != 0:
            self.prev_signal = self.signal
            if self.prev_indicator_tf1_f < self.prev_indicator_tf1_s and self.indicator_tf1_f > self.indicator_tf1_s:
                self.signal = 'LONG'
            elif self.prev_indicator_tf1_f > self.prev_indicator_tf1_s and self.indicator_tf1_f < self.indicator_tf1_s:
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
        self.contract.symbol = 'ES'
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
        print('Candle_TF1:', str(self.tick_count // self.ticks_per_candle_tf1+1).zfill(3),
              'Tick_TF1:', str(self.tick_count % self.ticks_per_candle_tf1 + 1).zfill(3),
              'Candle__TF2:', str(self.tick_count // self.ticks_per_candle_tf2+1).zfill(3),
              'Tick__TF2:', str(self.tick_count % self.ticks_per_candle_tf2 + 1).zfill(3),
              # 'Time:', datetime.datetime.fromtimestamp(time),
              "Price:", "{:.2f}".format(price),
              # 'Size:', size,
              'Ind_TF1_S:', "{:.2f}".format(self.indicator_tf1_s),
              'Prev_Ind_TF1_S:', "{:.2f}".format(self.prev_indicator_tf1_s),
              'Ind_TF1_F:', "{:.2f}".format(self.prev_indicator_tf1_f),
              'Prev_Ind_TF1_F:', "{:.2f}".format(self.prev_indicator_tf1_f),
              'Ind__TF2_S:', "{:.2f}".format(self.indicator_tf2_s),
              'Prev_Ind_TF2_S:', "{:.2f}".format(self.prev_indicator_tf2_s),
              'Ind_TF2_F:', "{:.2f}".format(self.indicator_tf2_f),
              'Prev_Ind_TF2_F:', "{:.2f}".format(self.prev_indicator_tf2_f),
              self.signal
        )
              # 'Data', self.data)
        if self.tick_count % self.ticks_per_candle_tf1 == self.ticks_per_candle_tf1 - 1:
            self.running_list_tf1_s(price)
            self.running_list_tf1_f(price)
            self.calc_prev_indicator_tf1_s()
            self.calc_indicator_tf1_s()
            self.calc_prev_indicator_tf1_f()
            self.calc_indicator_tf1_f()
            self.decision_engine()
            self.create_order()

        if self.tick_count % self.ticks_per_candle_tf2 == self.ticks_per_candle_tf2 - 1:
            self.running_list_tf2_s(price)
            self.running_list_tf2_f(price)
            self.calc_prev_indicator_tf2_s()
            self.calc_indicator_tf2_s()
            self.calc_prev_indicator_tf2_f()
            self.calc_indicator_tf2_f()

        self.tick_count += 1

def main():
    app = TestApp()
    app.connect("127.0.0.1", port=7497, clientId=101)
    print("serverVersion:%s connectionTime:%s" % (app.serverVersion(),app.twsConnectionTime()))
    app.run()

if __name__ == "__main__":
    main()