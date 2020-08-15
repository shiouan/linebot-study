import yfinance as yf


def get_stock(stock_id):
    tw_stock_id = f'{stock_id}.TW'
    rs = yf.Ticker(tw_stock_id)
    return rs
