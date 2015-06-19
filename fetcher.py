#fetcher.py
from zipline.api import record,symbol
import pandas as pd
# data = pd.read_csv('fetcher_sample_file.csv')
## This algo imports sample short interest data from a CSV file for one security, 
## NFLX, and plots the short interest:
def initialize(context):
    # fetch data from a CSV file somewhere on the web.
    # Note that one of the columns must be named 'symbol' for 
    # the data to be matched to the stock symbol
    fetch_csv('fetcher_sample_file.csv', date_column = 'Settlement Date',date_format = '%m/%d/%y')
    context.stock = symbol('NFLX')   
def handle_data(context, data):
    if 'Days To Cover' in data[context.stock]:
        record(Short_Interest = data[context.stock]['Days To Cover'])
