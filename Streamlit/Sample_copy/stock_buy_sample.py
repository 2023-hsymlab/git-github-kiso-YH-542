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

#各株銘柄取得＆最新(前日)の終値取得する関数
def get_kb_Close(code):
    end_date = dt.date.today()
    start_date = end_date + dt.timedelta(days=-3)
    stock_code = str(code) + '.JP'
    df = data.DataReader(stock_code,'stooq', start_date, end_date)
    kb_Close = df['Close']
    return kb_Close[0]

#買った時の価格(1株)を取得する関数
def buy_kb(code, buy_days):
    #表記：'%year-%month-%day
    enddate = buy_days
    startdate = enddate + dt.timedelta(days=-3)
    stock_code = str(code) + '.JP'
    df = data.DataReader(stock_code,'stooq', startdate, enddate)
    if df.empty:
        return None
    buy_kb_Close = df['Close']
    return buy_kb_Close[0]

#取引報告(買った場合[新しい株の購入])
def cal_kb(code, code_name, purchase_num, buy_days):
    connection = None
    passwordy = '507560yosshi'
    
    price = float(buy_kb(code, buy_days)) #買った時の一株あたりの単価
    # print(price)
    sum_price = float(price * purchase_num)
    # print(sum_price)
    info = 'buy' #売買の判断

    try:
        connection = mysql.connector.connect(
            host = 'localhost',
            user = 'yosshy',
            password = passwordy,
            database = 'stocks_situation'
        )

        cursor = connection.cursor()

        sql = ('''
        insert into transactions
            (stock_code, company_name, trade_situation, trade_day, amount, trade_price, sum_trade_price) 
            values (%s, %s, %s, %s, %s, %s, %s)
        ''')

        val = [
            (code, code_name, info, buy_days, purchase_num, price, sum_price)
        ]
        # print(val)

        cursor.executemany(sql, val)
        connection.commit()
        
        # print(f"MySQL INSERT success")

        cursor.close()
    except Error as err:
        print(f"Error:' {err}")
    
    finally:
        if connection is not None and connection.is_connected():
            connection.close()

#取引報告(買った場合[既存の株の購入])
def cal_kb_update(code, code_name, purchase_num, buy_days):
    connection = None
    passwordy = '507560yosshi'

    try:
        connection = mysql.connector.connect(
            host = 'localhost',
            user = 'yosshy',
            password = passwordy,
            database = 'stocks_situation'
        )

        cursor = connection.cursor()
        
        # 株式を持っているかチェックするクエリ
        check_sql = ('''
        SELECT COUNT(*) FROM transactions WHERE stock_code = %s
        ''')

        # 既存の株の情報を更新するクエリ
        update_sql = ('''
            UPDATE transactions
            SET trade_day = %s, amount = amount + %s
            WHERE stock_code = %s
        ''')


        # 株式を持っていない場合は新規購入として追加する
        cursor.execute(check_sql, (code,))
        result = cursor.fetchone()

        if result[0] == 0:
            cal_kb(code, code_name, purchase_num, buy_days)
            # st.write('新規購入しました!')
        else:
            cursor.execute(update_sql, (buy_days, purchase_num, code))
            connection.commit()
            # st.write('株数と購入日付を更新しました!')
        
        print(f"MySQL Update success")

        cursor.close()
    except Error as err:
        print(f"Error:' {err}")
    
    finally:
        if connection is not None and connection.is_connected():
            connection.close()

#保有株式の状況
def now_kb():
    connection = None
    passwordy = '507560yosshi'

    count = 0
    code_list = []
    company_list = []
    amount_list = []


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
            select id, stock_code, company_name, amount from transactions;
        ''')

        insert_sql = ('''
            insert into now_stocks
            (stock_code, company_name, now_price, amount, market_price, now_date)
            values (%s, %s, %s, %s, %s, %s)
        ''')

        cursor.execute(get_sql)
        
        for fetched_line in cursor.fetchall():
            id = fetched_line['id']
            # print(id)
            stock_code = fetched_line['stock_code']
            company_name = fetched_line['company_name']
            amount = fetched_line['amount']
            #保有株式のコードのリスト
            code_list.insert((id-1), stock_code)
            #保有株式の名前のリスト
            company_list.insert((id-1), company_name)
            #保有株式の保有数のリスト
            amount_list.insert((id-1), amount)
            count += 1

        # print(code_list)
        for i in range(count):
            code = int(code_list[i])
            code_name = company_list[i]
            amounts = int(amount_list[i])
            if code is None or amounts is None:
                continue
            now_price = float(get_kb_Close(code))
            # now_price = float(buy_kb(code, '2023-05-26'))
            # print(now_price)
            market_price = float(amounts * now_price)
            # now_date = dt.date.today() + dt.timedelta(days=-5)
            now_date = dt.date.today() + dt.timedelta(days=-1)
            val = [(code, code_name, now_price, amounts, market_price, now_date)]
            # print(f"{i+1}: MySQL INSERT success")
            # print(val)
            cursor.executemany(insert_sql, val)
            connection.commit()
            

        cursor.close()

    except Error as err:
        print(f"Error:' {err}")
    
    finally:
        if connection is not None and connection.is_connected():
            connection.close()


#### front部分 #####
## 参考：https://data-analytics.fun/2022/01/29/understanding-streamlit-1/
# https://data-analytics.fun/2022/06/26/streamlit-widget-1/#:~:text=%E3%83%9C%E3%82%BF%E3%83%B3%3A%20st.button,-%E3%81%BE%E3%81%9A%E3%80%81%E3%83%9C%E3%82%BF%E3%83%B3%E3%81%A7%E3%81%99&text=%E3%81%99%E3%82%8B%E3%81%A8%E3%80%81%E3%83%9C%E3%82%BF%E3%83%B3%E3%82%92%E6%8A%BC%E3%81%95%E3%82%8C,%E3%81%AB%E5%87%A6%E7%90%86%E3%82%92%E6%9B%B8%E3%81%8D%E3%81%BE%E3%81%99%E3%80%82&text=%E3%81%93%E3%82%8C%E3%81%A7click%20me!%E3%81%A8,%E3%81%99%E3%82%8B%E3%81%93%E3%81%A8%E3%81%8C%E3%81%A7%E3%81%8D%E3%81%BE%E3%81%99%E3%80%82
## https://docs.pyq.jp/python/pydata/streamlit.html


#タイトル表示
st.title("株売買画面")

# 企業コードを入力
stock_code_input = st.text_input('企業コードを入力: ')
stock_code = int(stock_code_input) if stock_code_input else None


# 企業名を入力
stock_name = st.text_input(
    '企業名を入力: ',
)

# 取引株数を入力
stock_amount_input = st.text_input('株数量を入力: ')
stock_amount = int(stock_amount_input) if stock_amount_input else None

# 取引情報
info_situation = st.radio(
    '取引情報',(
        '売','買'
	)
)

#取引日付
day_info = st.date_input(
    '取引日付: ',
    # デフォルト値は今日の日付
    dt.date.today()
)
st.write(day_info)

# 確認ボタン
k_button = st.button('確認')
# t_button = st.button('デバック用')

### 買う場合
##正しく入力されているかどうか判断     
if 'increment' not in st.session_state: # 初期化
    st.session_state['increment'] = 0

if k_button:
    if stock_code is None:
        st.write('企業コードを入力してください')
    elif not (stock_code >= 1000 and stock_code <= 9999):
        st.write('正しい企業コードを入力してください')
    elif stock_amount is None:
        st.write('株数量を入力してください')
    elif not stock_amount % 100 == 0:
        st.write('100株単位で入力してください')
    else:
        st.session_state['increment'] += 1
        st.write('この内容でよろしいですか')
        st.write(pd.DataFrame({
            '企業コード':[str(stock_code)],
            '企業名':[stock_name],
            '株数量':[stock_amount],
            '取引情報':[info_situation],
            '取引日付':[day_info]
		}))

# 買う場合       
if st.session_state['increment'] == 1 and info_situation == '買':
        col1, col2 = st.columns(2)
        with col1:
            yes_button = st.button('はい')
            if yes_button:
                cal_kb_update(stock_code, stock_name, stock_amount, day_info)
                with st.spinner():
                    time.sleep(3)
                    st.write('購入しました!')
                    st.session_state['increment'] = 0
        with col2:
            no_button = st.button('いいえ')
            if no_button:
                st.session_state['increment'] = 0
                st.write('修正してください')

# if t_button:
#     cal_kb(stock_code, stock_name, stock_amount, day_info)
#     st.write('購入しました!')

###売る場合
## 保有株数を全部売却する関数
def all_sell_stock(code, code_name, purchase_num):
    connection = None
    passwordy = '507560yosshi'
    
    count = 0
    judge = 0
    code_list = []
    company_list = []
    amount_list = []
    trade_day_list = []

    try:
        connection = mysql.connector.connect(
            host = 'localhost',
            user = 'yosshy',
            password = passwordy,
            database = 'stocks_situation'
        )

        cursor = connection.cursor(dictionary=True)
        
        get_sql = ('''
            select stock_code, company_name, trade_day, amount from transactions;
        ''')

        cursor.execute(get_sql)
        
        # この文で取得したテーブルのカラムにあるデータを全て取ってくる
        for fetched_line in cursor.fetchall():
            stock_code = fetched_line['stock_code']
            company_name = fetched_line['company_name']
            trade_day = fetched_line['trade_day']
            amount = fetched_line['amount']
            #保有株式のコードのリスト
            code_list.append(stock_code)
            #保有株式の名前のリスト
            company_list.append(company_name)
            #保有株式の保有数のリスト
            amount_list.append(amount)
            #保有株式を買った日付
            trade_day_list.append(trade_day)
            count += 1
        
        ##一旦、企業コードと企業名と保有株数が一致していたらその株をDBから消す
        delete_sql = ('''
            DELETE FROM transactions where stock_code = %s AND company_name = %s AND amount = %s;
        ''')
        ## 引数に一致する値がデータベースに存在しているかどうか
        ## 引数と一致する値が存在していたらjudgeに１を入れる
        for i in range(count):
            if code == code_list[i] and code_name == company_list[i] and purchase_num == amount_list[i]:
                judge = 1
        
        # judge = 1 ならDBから削除を実行
        if judge == 1:
            val = [(code, code_name, purchase_num)]
            cursor.executemany(delete_sql, val)
            connection.commit()
            # print(f"MySQL Delete success")
            
        # elif judge == 0:
        #     # print(f"正しい引数を入れてください")
        
        cursor.close()
        return judge

    except Error as err:
        print(f"Error:' {err}")
    
    finally:
        if connection is not None and connection.is_connected():
            connection.close()

## 保有株数を一部売却する関数
# 売却関数
def sell_stock(code, code_name, sell_num, trade_day):
    connection = None
    passwordy = '507560yosshi'
    check = 0

    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='yosshy',
            password=passwordy,
            database='stocks_situation'
        )

        cursor = connection.cursor()

        # 株式を持っているかチェックするクエリ
        check_sql = ('''
        SELECT COUNT(*) FROM transactions WHERE stock_code = %s
        ''')

        # 株式を売却するクエリ
        sell_sql = ('''
            UPDATE transactions
            SET trade_day = %s, amount = amount - %s
            WHERE stock_code = %s
        ''')

        # 株式を持っていない場合はエラーメッセージを表示
        cursor.execute(check_sql, (code,))
        result = cursor.fetchone()

        if result[0] == 0:
            print('売却する株式が存在しません。')
        else:
            # 株数が保有数を超える場合はエラーメッセージを表示
            cursor.execute('SELECT amount FROM transactions WHERE stock_code = %s', (code,))
            current_amount = cursor.fetchone()[0]
            if sell_num > current_amount:
                check = 0
            elif sell_num == current_amount:
                all_sell_stock(code, code_name, sell_num)
                check = 1
            else:
                cursor.execute(sell_sql, (trade_day, sell_num, code))
                connection.commit()
                check = 2

        cursor.close()
        return check
    except Error as err:
        print(f"Error: {err}")
    
    finally:
        if connection is not None and connection.is_connected():
            connection.close()



# 売る場合
if st.session_state['increment'] == 1 and info_situation == '売':
        col1, col2 = st.columns(2)
        with col1:
            yes_button = st.button('はい')
            if yes_button:
                stock_judge = sell_stock(stock_code, stock_name, stock_amount, day_info)
                with st.spinner():
                    time.sleep(3)
                    st.session_state['increment'] = 0
                    if stock_judge == 0:
                        st.write('売却する株数が保有数を超えています')
                    else:
                        st.write('売却しました')
        with col2:
            no_button = st.button('いいえ')
            if no_button:
                st.session_state['increment'] = 0
                st.write('修正してください')

### 現在の保有株一覧表示
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


"\b"

def get_stocks_name(df,name):
    company_code = []
    for i in range(len(df)):
        company_code.append(df.at[i, name])
    return company_code

#各株銘柄取得＆終値取得する関数
def get_kb_Close2(code, start_date, end_date):
    df = data.DataReader(code,'stooq', start_date, end_date)
    kb_Close = df['Close']
    return kb_Close

reload_button = st.button('更新')

if reload_button:
    now_df = see_stock()
    company_code = []
    company_name = []
    company_code = get_stocks_name(now_df, '企業コード') #企業コードが入っているリスト
    company_name = get_stocks_name(now_df, '企業名') #企業名が入っているリスト
    change_day = get_stocks_name(now_df, '取引日付') #取引日付が入っているリスト
    length = len(company_code) #保有している株の数

    df_change = pd.DataFrame()
    year = dt.date.today() + dt.timedelta(weeks=-52)
    for i in range(length):
        df_change = pd.concat([df_change, get_kb_Close2(str(company_code[i]) + '.JP', year, dt.date.today())], axis=1)
    
    df_change.columns = company_name
    df_change.index = pd.to_datetime(df_change.index) #日付データに変換
    df_change.to_csv("data/have_stocks.csv", encoding="shift_jis")

st.write('保有株一覧')
st.write(see_stock())

