import streamlit as st

from tabs.tab_1 import tab_1
from tabs.tab_2 import tab_2


st.set_page_config(
    page_title="EBT Dashboard 2027",
    page_icon="📊",
    layout="wide"
)


st.title("📊 EBT 2027")


# ==========================================================
# TABS
# ==========================================================

tab1, tab2 = st.tabs([
    "📋 Monitoring Proposal",
    "📊 Progress Matrix"
])


# ==========================================================
# TAB 1
# ==========================================================

with tab1:
    tab_1()


# ==========================================================
# TAB 2
# ==========================================================

with tab2:
    tab_2()