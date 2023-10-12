import streamlit as st
import mysql.connector
from mysql.connector import Error
import pandas as pd
from pandas_datareader import data
import datetime as dt

class SeeStock:

	def __init__(self):
		self.see_stock()
	
	###保有株数表示
	def see_stock(self):
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