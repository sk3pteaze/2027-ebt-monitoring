import streamlit as st


def show_kpi(df):

    # ==========================
    # HITUNG KPI
    # ==========================

    total_proposal = len(df)

    total_tahap1 = (
        df["TAHAPAN"] == "1"
    ).sum()

    total_tahap2 = (
        df["TAHAPAN"] == "2"
    ).sum()

    total_go = (
        df["TAHAPAN"] == "GO"
    ).sum()

    # ==========================
    # KPI
    # ==========================

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        if st.button(
            f"📋 TOTAL PROPOSAL\n\n{total_proposal:,}",
            use_container_width=True,
            key="kpi_total"
        ):
            st.session_state["kpi_filter"] = None

    with col2:

        if st.button(
            f"🟡 TAHAP 1\n\n{total_tahap1:,}",
            use_container_width=True,
            key="kpi_tahap1"
        ):
            st.session_state["kpi_filter"] = "1"

    with col3:

        if st.button(
            f"🟢 TAHAP 2\n\n{total_tahap2:,}",
            use_container_width=True,
            key="kpi_tahap2"
        ):
            st.session_state["kpi_filter"] = "2"

    with col4:

        if st.button(
            f"🔵 GO\n\n{total_go:,}",
            use_container_width=True,
            key="kpi_go"
        ):
            st.session_state["kpi_filter"] = "GO"

    return st.session_state.get(
        "kpi_filter",
        None
    )