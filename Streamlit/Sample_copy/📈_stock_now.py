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

from see_stock import SeeStock

class StocksNow:

	def __init__(self):
		st.title("保有株状況")
		###保有株数表示する
		self.now_df = SeeStock().see_stock()
		st.subheader('保有株一覧')
		reload_button = st.button('更新')
		st.dataframe(self.now_df,600,250)

if __name__ == '__main__':
    # インスタンスを作成し、ゲームを実行する
    stock_change = StocksNow()