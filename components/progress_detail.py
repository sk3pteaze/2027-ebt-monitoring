import streamlit as st


def show_progress_detail(df):

    if df.empty:
        return

    # ==========================
    # PILIH PROPOSAL
    # ==========================

    proposals = (
        df["NAMA PROPOSAL"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    proposals = sorted(proposals)

    if not proposals:
        return

    selected_proposal = st.selectbox(
        "📍 Pilih Proposal",
        options=proposals,
        index=None,
        placeholder="Pilih proposal...",
        key="selected_proposal"
    )

    if selected_proposal is None:
        return

    # ==========================
    # AMBIL DATA PROPOSAL
    # ==========================

    proposal_df = df[
        df["NAMA PROPOSAL"].astype(str)
        == selected_proposal
    ]

    if proposal_df.empty:
        return

    row = proposal_df.iloc[0]

    # ==========================
    # INFORMASI PROPOSAL
    # ==========================

    st.divider()

    st.subheader(
        f"📋 {selected_proposal}"
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.write("**SM**")
        st.write(row["LOCSM"])

    with col2:
        st.write("**RLM**")
        st.write(row["RLM"])

    with col3:
        st.write("**LOCAM**")
        st.write(row["LOCAM BARU"])

    with col4:
        st.write("**Cabang**")
        st.write(row["CAB"])

    # ==========================
    # PROGRESS
    # ==========================

    st.subheader("Progress")

    st.write(
        f"**Tahapan:** {row['TAHAPAN']}"
    )

    st.write(
        f"**Master Progress:** "
        f"{row['MASTER PROGRESS']}"
    )

    st.write(
        f"**Progress Proposal:** "
        f"{row['PROGRES PROPOSAL']}"
    )