import math
import numpy as np
from finta import TA
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px

import pandas as pd

from datetime import datetime


""" do WMA 9 (all ATR w/i 1 band) 21 or 34 (smooth trend) for daily or 9 for weekly n = 5 ATR = 21"""
""" do change period 45 or 15 or 6 on weeklies - go back to the place of trend change"""
""" WMA9 for 2 day bars with ATR 21 """

ticker = "ES=F"

# data = yf.download(tickers = ticker, start='2019-01-04', end='2021-06-09')
#data = yf.download(tickers = ticker, period = "2y", interval = '1wk')
data = yf.download(tickers = ticker, start='2000-01-04', end='2005-12-31', interval = '1d')

# valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
# valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
# https://pypi.org/project/yfinance/
# data = yf.download("SPY AAPL", start="2017-01-01", end="2017-04-30")

df1 = pd.DataFrame(data)

# print(df1)

df = df1.reset_index()

# print(df)

df7 = df.rename(columns = {'Date': 'date', 'Open':'open', 'High': 'high', 'Low':'low', 'Close':'close','Volume': 'volume'}, inplace = False)

# print(df7)
df7.to_csv('daily.csv')

n = 5

df3 = df7.groupby(np.arange(len(df7))//n).max()
# print('df3 max:', df3)

df4 = df7.groupby(np.arange(len(df7))//n).min()
# print('df4 min:', df4)

df5 = df7.groupby(np.arange(len(df7))//n).first()
# print('df5 open:', df5)

df6 = df7.groupby(np.arange(len(df7))//n).last()
# print('df6 close:', df6)


agg_df = pd.DataFrame()

agg_df['date'] = df6['date']
agg_df['low'] = df4['low']
agg_df['high'] = df3['high']
agg_df['open'] = df5['open']
agg_df['close'] = df6['close']

# print(agg_df)

df2 = agg_df

# print(df2)
num_periods = 21
df2['SMA'] = TA.SMA(df2, 21)
df2['FRAMA'] = TA.FRAMA(df2, 10)
df2['WMA'] = TA.WMA(df2, 9)
df2['TEMA'] = TA.TEMA(df2, num_periods)
# df2['VWAP'] = TA.VWAP(df2)

# how to get previous row's value
# df2['previous'] = df2['lower_band'].shift(1)

# ATR

# https://www.statology.org/exponential-moving-average-pandas/
num_periods_ATR = 21
multiplier = 1

df2['ATR_diff'] = df2['high'] - df2['low']
df2['ATR'] = df2['ATR_diff'].ewm(span=num_periods_ATR, adjust=False).mean()
# df2['ATR'] = df2['ATR_diff'].rolling(window=num_periods_ATR).mean()
df2['Line'] = df2['WMA']
# df2['line_change'] = df2['Line'] - df2['Line'].shift(1)
df2['line_change'] = df2['Line'] / df2['Line'].shift(1)
df3 = pd.DataFrame()
df3['date'] = df2['date']
df3['close'] = df2['line_change']
df3['open'] = df2['line_change']
df3['high'] = df2['line_change']
df3['low'] = df2['line_change']

periods_change = 1

df3['change_SMA'] = TA.SMA(df3, periods_change)
# df3.to_csv('sma_change.csv')
df2['change_SMA'] = df3['change_SMA']

df2['upper_band'] = df2['Line'] + multiplier * df2['ATR']
df2['lower_band'] = df2['Line'] - multiplier * df2['ATR']

multiplier_1 = 1.6
multiplier_2 = 2.3

df2['upper_band_1'] = df2['Line'] + multiplier_1 * df2['ATR']
df2['lower_band_1'] = df2['Line'] - multiplier_1 * df2['ATR']

df2['upper_band_2'] = df2['Line'] + multiplier_2 * df2['ATR']
df2['lower_band_2'] = df2['Line'] - multiplier_2 * df2['ATR']

# previous figures
# df2['upper_band_1_prev'] = df2['upper_band_1'].shift(1)
# df2['lower_band_1_prev'] = df2['lower_band_1'].shift(1)
# df2['upper_band_1_diff'] = df2['upper_band_1'] - df2['upper_band_1_prev']
# df2['lower_band_1_diff'] = df2['lower_band_1'] - df2['lower_band_1_prev']
# df2['upper_band_1_proj'] = df2['upper_band_1'] + df2['upper_band_1_diff']
# df2['lower_band_1_proj'] = df2['lower_band_1'] + df2['lower_band_1_diff']
# df2.loc[len(df2), 'lower_band_1'] = df2.loc[len(df2)-1, 'lower_band_1_proj']

# try the loop again
bars_back = 2
date_diff = df2.loc[len(df2)-1, 'date'] - df2.loc[len(df2)-2, 'date']

# line_diff = df2.loc[len(df2)-1, 'Line'] - df2.loc[len(df2)-bars_back, 'Line']
line_diff = df2.loc[len(df2)-1, 'change_SMA']

# upper_band_1_proj = df2.loc[len(df2)-1, 'upper_band_1'] + upper_band_1_diff
# df2.loc[len(df2), 'upper_band_1'] = upper_band_1_proj

counter = 0
bars_out = 20
while counter < bars_out:

    df2.loc[len(df2), 'Line'] = df2.loc[len(df2) - 1, 'Line'] * line_diff
    df2.loc[len(df2) - 1, 'date'] = df2.loc[len(df2) - 2, 'date'] + date_diff
    counter += 1

ATR = df2.loc[len(df2) - bars_out - 1, 'ATR'] * multiplier
ATR_1 = df2.loc[len(df2) - bars_out - 1, 'ATR'] * multiplier_1
ATR_2 = df2.loc[len(df2) - bars_out - 1, 'ATR'] * multiplier_2

counter1 = 0
while counter1 < bars_out:
    df2.loc[len(df2) - bars_out + counter1-1, 'upper_band_1'] = df2.loc[len(df2) - bars_out - 1 + counter1, 'Line'] + ATR_1
    df2.loc[len(df2) - bars_out + counter1-1, 'lower_band_1'] = df2.loc[len(df2) - bars_out - 1 + counter1, 'Line'] - ATR_1
    df2.loc[len(df2) - bars_out + counter1-1, 'upper_band_2'] = df2.loc[len(df2) - bars_out - 1 + counter1, 'Line'] + ATR_2
    df2.loc[len(df2) - bars_out + counter1-1, 'lower_band_2'] = df2.loc[len(df2) - bars_out - 1 + counter1, 'Line'] - ATR_2
    df2.loc[len(df2) - bars_out + counter1-1, 'upper_band'] = df2.loc[len(df2) - bars_out - 1 + counter1, 'Line'] + ATR
    df2.loc[len(df2) - bars_out + counter1-1, 'lower_band'] = df2.loc[len(df2) - bars_out - 1 + counter1, 'Line'] - ATR

    counter1 += 1

# df2.loc[len(df2), 'upper_band_1'] = df2.loc[len(df2)-1, 'upper_band_1'] + upper_band_1_diff
# df2.loc[len(df2)-1, 'lower_band_1'] = df2.loc[len(df2) - 2, 'lower_band_1'] + lower_band_1_diff # make sure this is one row higher
# df2.loc[len(df2) - 1, 'upper_band'] = df2.loc[len(df2) - 2, 'upper_band'] + upper_band_diff
# df2.loc[len(df2) - 1, 'lower_band'] = df2.loc[len(df2) - 2, 'lower_band'] + lower_band_diff
# df2.loc[len(df2) - 1, 'Line'] = df2.loc[len(df2) - 2, 'Line'] + line_diff
# df2.loc[len(df2) - 1, 'date'] = df2.loc[len(df2) - 2, 'date'] + date_diff
# counter += 1


print(df2.loc[len(df2) - bars_out - 1, 'ATR'])
# append dataframe
# https://stackoverflow.com/questions/53304656/difference-between-dates-between-corresponding-rows-in-pandas-dataframe
# https://www.geeksforgeeks.org/how-to-add-one-row-in-an-existing-pandas-dataframe/
# https://stackoverflow.com/questions/10715965/create-pandas-dataframe-by-appending-one-row-at-a-time
# https://stackoverflow.com/questions/49916371/how-to-append-new-row-to-dataframe-in-pandas
# https://stackoverflow.com/questions/50607119/adding-a-new-row-to-a-dataframe-why-loclendf-instead-of-iloclendf
# https://stackoverflow.com/questions/31674557/how-to-append-rows-in-a-pandas-dataframe-in-a-for-loop


print(df2[['date', 'upper_band', 'lower_band', 'upper_band_1','lower_band_1', 'Line']].tail(25))
print(df2.tail(25))

df2.to_csv("gauss.csv")

# https://community.plotly.com/t/how-to-plot-multiple-lines-on-the-same-y-axis-using-plotly-express/29219/9

# https://plotly.com/python/legend/#legend-item-names

# fig1 = px.scatter(df2, x='date', y=['close', 'open', 'high', 'low'], title='SPY Daily Chart')

fig1 = go.Figure(data=[go.Candlestick(x=df2['date'],
                open=df2['open'],
                high=df2['high'],
                low=df2['low'],
                close=df2['close'])]

)

fig1.add_trace(
    go.Scatter(
        x=df2['date'],
        y=df2['upper_band'],
        name='upper band',
        mode="lines",
        line=go.scatter.Line(color="gray"),
        showlegend=True)
)

fig1.add_trace(
    go.Scatter(
        x=df2['date'],
        y=df2['lower_band'],
        name='lower band',
        mode="lines",
        line=go.scatter.Line(color="gray"),
        showlegend=True)
)

fig1.add_trace(
    go.Scatter(
        x=df2['date'],
        y=df2['upper_band_1'],
        name='upper band_1',
        mode="lines",
        line=go.scatter.Line(color="gray"),
        showlegend=True)
)

fig1.add_trace(
    go.Scatter(
        x=df2['date'],
        y=df2['lower_band_1'],
        name='lower band_1',
        mode="lines",
        line=go.scatter.Line(color="gray"),
        showlegend=True)
)

fig1.add_trace(
    go.Scatter(
        x=df2['date'],
        y=df2['upper_band_2'],
        name='upper band_2',
        mode="lines",
        line=go.scatter.Line(color="gray"),
        showlegend=True)
)

fig1.add_trace(
    go.Scatter(
        x=df2['date'],
        y=df2['lower_band_2'],
        name='lower band_2',
        mode="lines",
        line=go.scatter.Line(color="gray"),
        showlegend=True)
)



fig1.add_trace(
    go.Scatter(
        x=df2['date'],
        y=df2['Line'],
        name="WMA",
        mode="lines",
        line=go.scatter.Line(color="blue"),
        showlegend=True)
)

fig1.update_layout(
    title = f'{ticker} Chart'
)

fig1.show()
