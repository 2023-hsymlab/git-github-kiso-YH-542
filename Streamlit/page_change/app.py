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

st.title('株式売買プログラム')

st.write('ログイン')

##ID入力
id_person = st.text_input('ID: ')

##password入力
password_person = st.text_input('password: ')