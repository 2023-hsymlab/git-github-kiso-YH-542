from pandas_datareader import data
import datetime as dt
import numpy as np
import pandas as pd
import time
import matplotlib.pyplot as plt
import matplotlib.style as style
# import mplfinance as mpf

#日付取得
end_date = dt.date.today()
start_date = end_date + dt.timedelta(weeks=-52)

code = ['9613.JP','9984.JP'] #ntt_data, softbank
name = ['NTT_Data','SoftBank']
# df_ntt = data.DataReader(code, 'stooq', start, end)

#各株銘柄取得＆終値取得する関数
def get_kb_Close(code, start_date, end_date):
    df = data.DataReader(code,'stooq', start_date, end_date)
    kb_Close = df['Close']
    return kb_Close

DF = pd.DataFrame()

for i in code:
    DF = pd.concat([DF, get_kb_Close(i, start_date, end_date)], axis=1)
DF.columns = name

DF.index = pd.to_datetime(DF.index)

DF_W = pd.DataFrame(DF.resample('W').last())
DF_W.plot(figsize=(7,7), linewidth = 1)

sxmin='2022-05-16'
sxmax='2023-05-16'
xmin = dt.datetime.strptime(sxmin, '%Y-%m-%d')
xmax = dt.datetime.strptime(sxmax, '%Y-%m-%d')
plt.xlim([xmin,xmax])

