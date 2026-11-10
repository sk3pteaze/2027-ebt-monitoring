import streamlit as st

from data.loader import load_data
from components.progress_matrix import show_progress_matrix


def tab_2():



    df = load_data()

    if df is None or df.empty:
        st.info("Data belum tersedia.")
        return

    # Tidak menggunakan filter RLM / LOCAM
    show_progress_matrix(df)