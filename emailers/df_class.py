import yfinance as yf
import pandas as pd

# https://stackoverflow.com/questions/21800169/python-pandas-get-index-of-rows-which-column-matches-certain-value
# https://stackoverflow.com/questions/51571121/how-to-select-rows-which-values-start-and-end-with-a-specific-value-in-pandas
# https://davidhamann.de/2017/06/26/pandas-select-elements-by-string/
# https://www.interviewqs.com/ddi-code-snippets/rows-cols-python
# https://stackoverflow.com/questions/41217310/get-index-of-a-row-of-a-pandas-dataframe-as-an-integer

# data = yf.download(tickers = ticker, start='2019-01-04', end='2021-06-09')

class Sample_DF_Call:

    def __init__(self):
        self.select_to_end = 0

    def yahoo_sample(self):
        ticker = 'NQ=F'
        data = yf.download(tickers=ticker, period="3mo", interval='1wk')
        df = pd.DataFrame(data)
        df = df.reset_index()
        selected_date = df['Date'] == '2021-06-21'
        selected_row = df.loc[selected_date]
        selected_index = int(df[selected_date].index[0])

        print(selected_row)
        print(selected_index)
        self.select_to_end = df[selected_index:len(df)]
        print(self.select_to_end)
        self.select_to_end.to_csv('select_to_end.csv')

        # print(df[['Date', 'Close']].tail(3))
