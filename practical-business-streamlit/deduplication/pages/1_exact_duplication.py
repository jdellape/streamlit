import streamlit as st
import pandas as pd
from collections import Counter

st.set_page_config(page_title="Exact Duplication")

uploaded_file = st.file_uploader("Choose a file (accepting .csv files only at the moment)")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.write("Duplicated rows below: ")
    st.write(df[df.duplicated()])
