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

## イメージ
# 	株購入画面
# 	株購入の情報を入力
# 	確認ボタンを押す
# 		↓ページ遷移
# 	確認画面に移動
# 	はい	or	いいえ
# 		↓ページ遷移
# 	購入完了     購入画面に戻る
# 		↓ページ遷移
# 	株購入画面に戻る

#-----株の売買に関する関数----#
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

#-----フロント部分------#
## session_state
#   タブ上で更新や再実行が発生した際に，前後で変数の値を共有するための方法

# init
def init():
    #sessionの状態を初期化
    ##session_stateにinitがない場合はinitを追加し、Trueを入れる
    ## その後,reset_session,countを実行
    if "init" not in st.session_state:
        st.session_state.init=True
        reset_session()
        return True
    else:
        return False

def tab_session():
    #session_state.now_tabの値とst.session_state.tabの値が違う場合reset_session実行
    if not st.session_state.now_tab==st.session_state.tab:
        reset_session()
    st.session_state.now_tab=st.session_state.tab

##ページ管理
def layer_session(layer=0):
    st.session_state.layer=layer

##ページリセット
def reset_session():
    st.session_state.now_tab=None
    layer_session()

def back_btn():
    st.button("戻る。",on_click=reset_session)

def select_btn():
    col1, col2 = st.columns(2)
    with col1:
        yes_button = st.button('はい')
        if yes_button:
            print(st.session_state.stock_code)
            print(st.session_state.info_situation)
            if st.session_state.info_situation == '買':
                cal_kb_update(st.session_state.stock_code, st.session_state.stock_name, st.session_state.stock_amount, st.session_state.day_info)
                with st.spinner():
                    time.sleep(3)
                    st.write('購入しました!')
                    col1.empty()
                    st.session_state.increment = 0
                    back_btn()
            if st.session_state.info_situation == '売':
                stock_judge = sell_stock(st.session_state.stock_code, st.session_state.stock_name, st.session_state.stock_amount, st.session_state.day_info)
                with st.spinner():
                    time.sleep(3)
                    st.session_state['increment'] = 0
                    if stock_judge == 0:
                        st.write('売却する株数が保有数を超えています')
                        col1.empty()
                        st.session_state.increment = 0
                        back_btn()
                    else:
                        st.write('売却しました')
                        col1.empty()
                        st.session_state.increment = 0
                        back_btn()

    with col2:
        no_button = st.button('いいえ', on_click=reset_session)
        st.session_state.increment = 0

def pop_btn(label="pop",key=None, layer=0, onclick=lambda:None, done=None, description=None):
    placeholder=st.empty()
    with placeholder.container():
        if description:
            st.write(description)
        res=st.button(label,key=key,on_click=lambda:[placeholder.empty(),layer_session(layer),onclick()])
    if res:
        if done:
            with placeholder:
                done()
                # placeholder.empty()

def pop(msg, done=None, interval=1):
    with st.spinner(msg):
        time.sleep(interval)
    if done:
        done()

st.title('株購入画面')

## contents
def index():
    # 企業コードを入力
    stock_code_input = st.text_input('企業コードを入力: ')
    stock_code = int(stock_code_input) if stock_code_input else None


    # 企業名を入力
    stock_name = st.text_input(
        '企業名を入力: '
    )

    # 取引株数を入力
    stock_amount_input = st.text_input('株数量を入力: ')
    stock_amount = int(stock_amount_input) if stock_amount_input else None

    # 取引情報
    info_situation = st.radio(
        '取引情報',(
            '買','売'
        )
    )

    #取引日付
    day_info = st.date_input(
        '取引日付: ',
        # デフォルト値は今日の日付
        dt.date.today()
    )

    st.session_state.stock_code = stock_code
    st.session_state.stock_name = stock_name
    st.session_state.stock_amount = stock_amount
    st.session_state.info_situation = info_situation
    st.session_state.day_info = day_info
    

def confirm(i):
    if st.session_state.layer == 0 or st.session_state.layer == 1:
        index()       

    pop_btn(
        label="確認",
        layer=i,
        onclick=lambda:None,
        done=lambda:[
            check()
        ]
    )
    # check_judge()

def check():
    if 'increment' not in st.session_state: # 初期化
        st.session_state.increment = 0

    if st.session_state.stock_code is None:
        st.write('企業コードを入力してください')
    elif not (st.session_state.stock_code >= 1000 and st.session_state.stock_code <= 9999):
        st.write('正しい企業コードを入力してください')
    elif st.session_state.stock_amount is None:
        st.write('株数量を入力してください')
    elif not st.session_state.stock_amount % 100 == 0:
        st.write('100株単位で入力してください')
    else:
        st.session_state.increment += 1
        print(st.session_state.increment)
        st.write('この内容でよろしいですか')
        stock_data = pd.DataFrame({
            '企業コード':[str(st.session_state.stock_code)],
            '企業名':[st.session_state.stock_name],
            '株数量':[st.session_state.stock_amount],
            '取引情報':[st.session_state.info_situation],
            '取引日付':[st.session_state.day_info]
		})
        st.dataframe(stock_data, 600, 250)

def check_judge():
    if st.session_state.stock_code is None:
        back_btn()
    elif not (st.session_state.stock_code >= 1000 and st.session_state.stock_code <= 9999):
        back_btn()
    elif st.session_state.stock_amount is None:
        back_btn()
    elif not st.session_state.stock_amount % 100 == 0:
        back_btn()
    else:
        st.write('この内容でよろしいですか')
        select_btn()


init()

st.session_state.tab = 'stock_buy'
_tab=st.session_state.tab
_layer=st.session_state.layer
if _tab=="stock_buy":
    if _layer==0 or _layer == 1:
        layer_session(1)
        confirm(2)
        print(_layer)
        print(st.session_state.stock_code)
    elif _layer==2:
        st.info(f"確認画面です")
        confirm(2)
        check_judge()
        print(st.session_state.stock_code)
