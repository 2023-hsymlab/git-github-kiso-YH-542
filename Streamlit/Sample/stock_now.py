import streamlit as st
import mysql.connector
from mysql.connector import Error
import pandas as pd
from pandas_datareader import data
import datetime as dt
import numpy as np
import time
import matplotlib.pyplot as plt
import matplotlib.style as style
import asyncio

### 保有している株の状況をグラフや表で表示するページ
#タイトル表示
st.title("保有株状況")
###保有株数表示
def see_stock():
    connection = None
    passwordy = '507560yosshi'
    now_stock_list = []

    try:
        connection = mysql.connector.connect(
            host = 'localhost',
            user = 'yosshy',
            password = passwordy,
            database = 'stocks_situation'
        )

        cursor = connection.cursor(dictionary=True)
        #trade_situationの判定をしない場合(仮)
        get_sql = ('''
            select stock_code, company_name, trade_day, amount from transactions;
        ''')

        cursor.execute(get_sql)
        
        for fetched_line in cursor.fetchall():
            stock_code = str(fetched_line['stock_code'])
            company_name = fetched_line['company_name']
            trade_day = fetched_line['trade_day']
            amount = fetched_line['amount']
            now_stock_list.append([stock_code, company_name, amount, trade_day])
        
        colums = ["企業コード", "企業名", "保有株数", "取引日付"]
        df = pd.DataFrame(data=now_stock_list, columns=colums)
        
        # print(now_stock_list)

        cursor.close()

        return df

    except Error as err:
        print(f"Error:' {err}")
    
    finally:
        if connection is not None and connection.is_connected():
            connection.close()

now_df = see_stock()
st.subheader('保有株一覧')
reload_button = st.button('更新')

st.dataframe(now_df,600,250)

#前日比の価格を出す関数
def stock_metric(df,name):
    now_stock = df.iloc[0][name] #指定の株の現在価格を取得
    yesday_stock = df.iloc[1][name]#前日の価格を取得
    delta = now_stock - yesday_stock
    return delta

##保有株の変動をグラフで表示する
###まず、保有株の企業コードを取得する
def get_stocks_name(df,name):
    company_code = []
    for i in range(len(df)):
        company_code.append(df.at[i, name])
    return company_code

#各株銘柄取得＆終値取得する関数
def get_kb_Close(code, start_date, end_date):
    df = data.DataReader(code,'stooq', start_date, end_date)
    kb_Close = df['Close']
    return kb_Close

now_df = see_stock()
##保有している株の情報をリストに取得
company_code = []
company_name = []
company_code = get_stocks_name(now_df, '企業コード') #企業コードが入っているリスト
company_name = get_stocks_name(now_df, '企業名') #企業名が入っているリスト
change_day = get_stocks_name(now_df, '取引日付') #取引日付が入っているリスト
length = len(company_code) #保有している株の数

#更新が押された時にCSVの内容を更新
if reload_button:
    #df_changeに保有株の一年分のデータを入れる
    df_change = pd.DataFrame()
    year = dt.date.today() + dt.timedelta(weeks=-52)
    for i in range(length):
        df_change = pd.concat([df_change, get_kb_Close(str(company_code[i]) + '.JP', year, dt.date.today())], axis=1)
    
    df_change.columns = company_name
    df_change.index = pd.to_datetime(df_change.index) #日付データに変換
    df_change.to_csv("data/have_stocks.csv", encoding="shift_jis")
    st.write(str(dt.date.today())+ '  時点での状況')

st.subheader('前日比')
#前日比の価格
num_columns = len(company_name)
num_cols_per_row = 4
num_rows = (num_columns - 1) // num_cols_per_row + 1

##csvを読み込んで取引日付、1ヶ月前、6ヶ月前、1年前とそれぞれのデータフレームに分割する
###csvの読み込みの参考　https://note.nkmk.me/python-pandas-read-csv-tsv/
df_year = pd.read_csv('data/have_stocks.csv', index_col=0, encoding='shift_jis')
df_month = pd.read_csv('data/have_stocks.csv', index_col=0, nrows=22, encoding='shift_jis')
df_sixmonth = pd.read_csv('data/have_stocks.csv', index_col=0, nrows=127, encoding='shift_jis')
##取引日付
year_ago = dt.date.today() + dt.timedelta(weeks=-52)
day_judge = False
if change_day:
    day_exchange = change_day[0] #古い日付を入れる
    for i in range(length):
        #取引日付が1年前より前かどうか
        day_judge = (year_ago > change_day[i])
        ##日付の比較
        if day_exchange >= change_day[i]:
            day_exchange = change_day[i] ##一番昔の日付が入る

if day_judge == True:
    df_exchange = df_year
else:
    today = dt.date.today()
    dif_day = today - day_exchange
    # print(day_exchange)
    # print(today)
    # print(dif_day.days)
    df_exchange = pd.read_csv('data/have_stocks.csv', index_col=0, nrows= int(dif_day.days)+1, encoding='shift_jis')

#前日比との価格を４企業ずつ改行しながら表示する部分
cols = st.columns(num_cols_per_row)
for i, col_index in enumerate(range(num_cols_per_row)):##例)num_cols_per_now(0,1,2,3)
    for j, row_index in enumerate(range(num_rows)):##例)num_rows(0,1)
        index = col_index + row_index * num_cols_per_row
        if index < num_columns:
            col = cols[i]
            name = company_name[index]
            value = df_exchange.iloc[0][name]
            delta = stock_metric(df_exchange, name)
            col.metric(label=name, value=f'{value} 円', delta=f'{delta} 円')

"\b"
#----- グラフ表示 ------#
st.subheader('保有株の株推移')

# タブの表示
tab1, tab2, tab3, tab4 = st.tabs(["最も過去の取引日付から", "1ヶ月前", "6ヶ月前", "1年前"])

with tab1:
    # タブが選択されたらグラフを表示
	st.line_chart(df_exchange)

with tab2:
    # タブが選択されたらグラフを表示
    st.line_chart(df_month)


with tab3:
    # タブが選択されたらグラフを表示
    st.line_chart(df_sixmonth)


with tab4:
    # タブが選択されたらグラフを表示
    st.line_chart(df_year)


st.write('Checkbox仮')
col_company = st.columns(length)
company_checkbox = []


# スライダーで表示範囲を選択
num_days = len(df_year)  # データフレームの日数を取得
time_range = st.slider("表示範囲を選択してください", min_value=1, max_value=num_days, value=num_days, step=1, format="%d 日前")

# 選択された表示範囲に応じてデータを抽出
selected_df = df_year.head(time_range)
# print(time_range)

# チェックボックスの状態を取得
for i in range(length):
    company_checkbox.append(col_company[i].checkbox(label=company_name[i]))

# チェックボックスがチェックされている要素のインデックスを取得
checked_indices = [i for i, checkbox in enumerate(company_checkbox) if checkbox]
# print(checked_indices)
# チェックボックスがチェックされている要素のデータフレームを抽出
selected_stocks = selected_df.iloc[:, checked_indices]

# 選択された株式の価格推移をグラフで表示
st.line_chart(selected_stocks)



