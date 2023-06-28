import streamlit as st

st.title("hello")
st.button("button1")
st.selectbox("selectbox", ("sele1", "sele2"))

check = st.checkbox("check button") # チェックボタン

if check:
  st.button("button")
  st.selectbox("selectbox", ("select1", "select2"))
  st.multiselect("multiselectbox", ("select1", "select2"))
  st.radio("radiobutton", ("radio1", "radio2"))
  st.text_input("text input")
  st.text_area("text area")
  st.slider("slider", 0, 100, 50)
  st.file_uploader("Choose file")