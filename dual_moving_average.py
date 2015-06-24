#dual_moving_average.py
#!/usr/bin/env python
#
# Copyright 2014 Quantopian, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Dual Moving Average Crossover algorithm.
This algorithm buys apple once its short moving average crosses
its long moving average (indicating upwards momentum) and sells
its shares once the averages cross again (indicating downwards
momentum).
"""

from zipline.api import order_target, record, symbol, history, add_history,order
from zipline import TradingAlgorithm
import matplotlib.pyplot as plt
import pandas as pd
def initialize(context):
    # Register 2 histories that track daily prices,
    # one with a 100 window and one with a 300 day window
    #add_history(100, '1m', 'price')
    #add_history(300, '1m', 'price')
    context.i = 0
    context.sym = 'Close'

def handle_data(context, data):
    # Skip first 300 days to get full windows
    #print data['Close'].dt
    #context.i += 1
    #if context.i < 300:
    #    return
    # Compute averages
    # history() has to be called with the same params
    # from above and returns a pandas dataframe.
    sym = symbol('Close')
    if data['short_mavg'].price > data['long_mavg'].price:
        # order_target orders as many shares as needed to
        # achieve the desired number of shares.
        order_target(context.sym, 1000)
    elif data['short_mavg'].price < data['long_mavg'].price:
        order_target(context.sym, 0)


    # Save values for later inspection
    record(Close=data[context.sym].price,
           short_mavg=data['short_mavg'].price,
           long_mavg=data['long_mavg'].price)

def analyze(context, perf):
    fig = plt.figure()
    ax1 = fig.add_subplot(211)
    perf.portfolio_value.plot(ax=ax1)
    ax1.set_ylabel('portfolio value in $')

    ax2 = fig.add_subplot(212)
    perf['AAPL'].plot(ax=ax2)
    perf[['short_mavg', 'long_mavg']].plot(ax=ax2)

    perf_trans = perf.ix[[t != [] for t in perf.transactions]]
    buys = perf_trans.ix[[t[0]['amount'] > 0 for t in perf_trans.transactions]]
    sells = perf_trans.ix[
        [t[0]['amount'] < 0 for t in perf_trans.transactions]]
    ax2.plot(buys.index, perf.short_mavg.ix[buys.index],
             '^', markersize=10, color='m')
    ax2.plot(sells.index, perf.short_mavg.ix[sells.index],
             'v', markersize=10, color='k')
    ax2.set_ylabel('price in $')
    plt.legend(loc=0)
    plt.show()

if __name__ == '__main__':
    import pylab as pl
    # Read data from yahoo website
    #start = datetime(2008, 1, 1, 0, 0, 0, 0, pytz.utc)
    #end = datetime(2010, 1, 1, 0, 0, 0, 0, pytz.utc)
    #data = load_from_yahoo(stocks=['AAPL'], indexes={}, start=start,end=end)
    #data = data.dropna()
    
    # Read data from csv
    data = pd.read_csv('EURUSD.csv') # DataFrame
    data = data.dropna()
    data.set_index('Date', inplace=True) # set the Date as index
    data.index = pd.to_datetime(data.index, utc=True) # convert to datetime format
    print data.head()
    # Or directly
    #data = pd.DataFrame.from_csv('AAPL.csv')

    data['short_mavg'] = pd.rolling_mean(data['Close'], 100)
    data['long_mavg'] = pd.rolling_mean(data['Close'], 300)

    algo = TradingAlgorithm(initialize=initialize,
                            handle_data=handle_data)
                            #identifiers=['AAPL'])
    results = algo.run(data)
    results.to_csv('EURUSD_DMA.csv')