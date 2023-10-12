## 参考：https://qiita.com/gudapys/items/cae2730f093879659d1f 
import streamlit as st
import time

# config
# 詳細:https://data-analytics.fun/2022/07/10/streamlit-theme-page-settings/

## ページの詳細情報の部分
st.set_page_config(
    page_title="Streamlit テンプレート",
    layout="wide",
    initial_sidebar_state="expanded"
)

## init等で使われているsession_stateの変数
# st.session_state.init
# st.session_state.now_tab
# st.session_state.tab
# st.session_state.layer
# st.session_state.count

# init
def init():
    #sessionの状態を初期化
    ##session_stateにinitがない場合はinitを追加し、Trueを入れる
    ## その後,reset_session,countを実行
    if "init" not in st.session_state:
        st.session_state.init=True
        reset_session()
        count()
        return True
    else:
        return False


def tab_session():
    #session_state.now_tabの値とst.session_state.tabの値が違う場合reset_session実行
    if not st.session_state.now_tab==st.session_state.tab:
        reset_session()
    st.session_state.now_tab=st.session_state.tab
def layer_session(layer=0):
    st.session_state.layer=layer
def reset_session():
    st.session_state.now_tab=None
    layer_session()

# extends
def count():
    if "count" not in st.session_state:
        st.session_state.count=0
    st.session_state.count+=1

# UI components
def deco_horizontal(func):
    def wrapper(*args, **kwargs):
        st.write("---")
        func(*args, **kwargs)
        st.write("---")
    return wrapper

@deco_horizontal
def back_btn():
    st.button("戻る。",on_click=reset_session)

def btn(label="ボタン",key=None,onclick=None,done=None):
    if st.button(label,key=key,on_click=onclick) and done:
        done()

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
                placeholder.empty()

def pop(msg, done=None, interval=1):
    with st.spinner(msg):
        time.sleep(interval)
    if done:
        done()

# contents
def index():
    st.write("ここは **Indexページ** です。")

def sample_content(i):
    st.write(f"ここは **ページ {i}** です。")
    pop_btn(
        label="POPボタン",
        layer=2,
        onclick=lambda:[count()],
        done=lambda:[
            pop("POPボタンが押されました"),
            st.success("成功！"),
            time.sleep(1)
        ]
    )

# body
init()

##ここでsession_state.tabにIndexかListが入る
st.session_state.tab = st.sidebar.selectbox("選択してください。", ["Index","List"])
print(st.session_state.tab)
tab_session()# TAB切り替えの管理
# delay
time.sleep(0.1)

_tab=st.session_state.tab
_layer=st.session_state.layer
if _tab=="Index":
    if _layer==0 or _layer==1:
        layer_session(1)
        index()
elif _tab=="List":
    if _layer==0 or _layer==1:
        layer_session(1)
        sample_content(1)
    elif _layer==2:
        st.info(f"POPによるページ遷移をしました。")
        sample_content(1)
        back_btn()

# monitor
st.sidebar.write("### Monitor")
st.sidebar.write(f"tab = \"{st.session_state.tab}\"")
#st.sidebar.write(f"now_tab = \"{st.session_state.now_tab}\"")
st.sidebar.write(f"layer = {st.session_state.layer}")
st.sidebar.write(f"count = {st.session_state.count}")
