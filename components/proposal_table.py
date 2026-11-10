import streamlit as st


def proposal_selector(df):

    if df.empty:
        st.info("Tidak ada proposal.")
        return None

    # ==========================
    # DAFTAR PROPOSAL
    # ==========================

    proposals = (
        df["NAMA PROPOSAL"]
        .dropna()
        .astype(str)
        .str.strip()
    )

    proposals = sorted(
        proposals[
            proposals != ""
        ].unique()
    )

    if not proposals:
        st.info("Tidak ada proposal.")
        return None

    # ==========================
    # SELECTBOX
    # ==========================

    selected = st.selectbox(
        "📍 Pilih Proposal",
        options=proposals,
        index=None,
        placeholder="Pilih proposal...",
        key="proposal_selector"
    )

    return selected