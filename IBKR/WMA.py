import math
import pandas as pd
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
# types
from ibapi.common import *  # @UnusedWildImport
from ibapi.contract import * # @UnusedWildImport
from ibapi.order import Order
import datetime
from finta import TA

MOVING_AVG_PERIOD_LENGTH = 3
TICKS_PER_CANDLE = 4

class TestApp(EWrapper, EClient):
    def __init__(self):
        EWrapper.__init__(self)
        EClient.__init__(self, wrapper=self)
        self.nextValidOrderId = None
        self.permId2ord = {}
        self.contract = Contract()
        self.data = []
        self.data_counter = 0
        self.df = pd.DataFrame()
        self.data1 = []
        self.df1 = pd.DataFrame()
        self.recent_price = 0
        self.cash_value = 0
        self.num_shares = 0
        self.safety_num_shares = 0
        self.shares_to_buy = 0
        self.num_contracts = 0
        self.mov_avg_length = MOVING_AVG_PERIOD_LENGTH
        self.ticks_per_candle = TICKS_PER_CANDLE
        self.tick_count = 0
        self.num_shares_live = 0
        self.wma = 0


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
        self.accountOperations_req()
        print("Executing requests ... finished")

    def accountOperations_req(self):
        # Requesting accounts' summary
        # ! [reqaaccountsummary]
        self.reqAccountSummary(9002, "All", "$LEDGER")
        # ! [reqaaccountsummary]

    # ! [accountsummary]
    def accountSummary(self, reqId: int, account: str, tag: str, value: str,
                       currency: str):
        super().accountSummary(reqId, account, tag, value, currency)
        # print("AccountSummary. ReqId:", reqId, "Account:", account,
        #       "Tag: ", tag, "Value:", value, "Currency:", currency)
        self.data1.append([tag, value])
        self.df1 = pd.DataFrame(self.data1, columns=['Account', 'Value'])
        if len(self.df1) == 24:
            # print(self.df1)
            self.df1.to_csv('acct_value.csv')
            self.cash_value = self.df1.loc[2, 'Value']

    def running_list(self, price: float):
        self.data.append(price)
        self.data_counter += 1
        if self.data_counter < self.mov_avg_length:
            return
        while len(self.data) > self.mov_avg_length:
            self.data.pop(0)

    def calc_wma(self):
        df_wma = pd.DataFrame(self.data, columns=['close'])
        df_wma['open'] = df_wma['close']
        df_wma['high'] = df_wma['close']
        df_wma['low'] = df_wma['close']
        df_wma['sma'] = TA.SMA(df_wma, self.mov_avg_length)
        self.wma = df_wma['sma'].iloc[-1]

    def sma(self):
        sma = sum(self.data) / len(self.data)

    def calc_contracts(self, price: float):
        # self.running_list()
        if len(self.data) > 0:
            self.num_shares_live = float(self.cash_value) / (price / 100) # get rid of 100 for stock
            self.safety_num_shares = 0.75 * self.num_shares_live
            self.shares_to_buy = math.floor(self.safety_num_shares / 100) * 100
            self.num_contracts = self.shares_to_buy / 100

    def sendOrder(self, action):
        # Create contract object
        self.contract.symbol = 'NQ'
        self.contract.secType = 'FUT'
        self.contract.exchange = 'GLOBEX'
        self.contract.currency = 'USD'
        self.contract.lastTradeDateOrContractMonth = "202109"

        order = Order()
        order.action = action
        order.totalQuantity = 1
        order.orderType = "MKT"
        self.placeOrder(self.nextOrderId(), self.contract, order)

    def check_and_send_order(self):
        self.sendOrder('BUY')

    def tickDataOperations_req(self):
        # Create contract object
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
              'Time:', datetime.datetime.fromtimestamp(time),
              "Price:", "{:.2f}".format(price),
              'Size:', size,
              'Cash:',self.cash_value,
              'Full Shares:',"{:.2f}".format(self.num_shares_live),
              'Partial Shares:',self.shares_to_buy,
              'Contracts:',self.num_contracts,
              'WMA:', "{:.2f}".format(self.wma),
              'Data', self.data)
        if self.tick_count % self.ticks_per_candle == self.ticks_per_candle - 1:
            self.running_list(price)
            self.calc_wma()
            self.calc_contracts(price)
        self.tick_count += 1

def main():
    app = TestApp()
    app.connect("127.0.0.1", port=7497, clientId=102)
    print("serverVersion:%s connectionTime:%s" % (app.serverVersion(),app.twsConnectionTime()))
    app.run()

if __name__ == "__main__":
    main()