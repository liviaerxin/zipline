import pandas as pd
import locale
import matplotlib.pyplot as plt
from zipline.algorithm import TradingAlgorithm
import zipline.finance.trading as trading
from zipline.utils.factory import load_from_yahoo
from datetime import datetime, date
from pytz import timezone
import pytz
from dateutil.tz import tzutc
from dateutil.parser import parse
from zipline.finance.slippage import FixedSlippage
from zipline.finance.commission import PerShare, PerTrade


HOLDTIME = 5
COMMISSION=0.005


class BollingerBands(TradingAlgorithm):   

    def initialize(self):
        self.invested = False
        self.trade_size=1000
        self.long = False
        self.short = False
        self.closed = False
        self.trading_day_counter = 0  
        self.pct_stop = 0.025
        self.long_stop_price =  0.0
        self.short_stop_price=0.0
        self.target=0.05
        commission_cost = self.trade_size * COMMISSION
        self.set_slippage(FixedSlippage(spread=0.10))  
        self.set_commission(PerTrade(cost=commission_cost))  

    def handle_data(self, data):


        if data['Close'].price >= data['upper'].price and not self.invested:
            self.order('Close', self.trade_size)
            self.long_stop_price =  data['Open'].price - data['Open'].price * float(self.pct_stop) 
            self.short_stop_price =  data['Open'].price + data['Open'].price * float(self.target)
            self.long = True
            self.closed=False
            self.invested = True
            self.trading_day_counter = 0  
        if data['Close'].price <= data['lower'].price and not self.invested:
            self.short_stop_price =  data['Open'].price + data['Open'].price * float(self.pct_stop)
            self.long_stop_price =  data['Open'].price - data['Open'].price * float(self.target) 
            self.order('Close', -self.trade_size)
            self.short = True
            self.closed=False
            self.invested = True
            self.trading_day_counter = 0  
        if self.invested and (data['Close'].price <=  self.long_stop_price or data['Close'].price >=  self.short_stop_price): #or self.trading_day_counter == HOLDTIME):

            if self.long: 
                self.order('Close', -self.trade_size)
            if self.short:
                self.order('Close', self.trade_size)
            self.closed=True
            self.long=False
            self.short=False
            self.invested=False


        self.trading_day_counter =  self.trading_day_counter +1
        self.record(Close=data['Close'].price,
                    upper=data['upper'].price,
                    lower=data['lower'].price,
                    long=self.long,
                    short=self.short,
                    holdtime=self.trading_day_counter,
                    closed_position=self.closed,
                    shares=self.trade_size)


if __name__ == '__main__':
    df = pd.read_csv('EURUSD.csv') # DataFrame
    df = df.dropna()
    df.set_index('Date', inplace=True) # set the Date as index
    df.index = pd.to_datetime(df.index, utc=True) # convert to datetime format

    df['avg'] = pd.rolling_mean(df['Close'], 21)
    df['std'] = pd.rolling_std(df['Close'], 21)
    df['upper'] = df['avg'] + 2 * df['std']
    df['lower'] = df['avg'] - 2 * df['std']
    df = df.dropna()

    # # # # init Strat Class
    Strategy = BollingerBands()
    # #print df

    # # # # # # Run Strategy
    results = Strategy.run(df)
    results['algorithm_returns'] = (1 + results.returns).cumprod()


    results.to_csv('EURUSD_Bollinger.csv')
    print results['algorithm_returns'].tail(1)[0]*100
