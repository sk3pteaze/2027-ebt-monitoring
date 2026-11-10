import streamlit as st


# ==========================================================
# URUTAN MAPPING PROGRESS
# ==========================================================

PROGRESS_ORDER = [
    "SERAH TERIMA PROJECT",
    "RENOVASI",
    "NOTARIS",
    "RENCANA NOTARIS",
    "IZIN",
    "PROPOSAL ACC",
    "PROP HO - DIREKSI",
    "PROP HO - AUDIT",
    "PROP HO - LOC",
    "PANEL FINAL OK",
    "PANEL FINAL NOTE",
    "SIAP PANEL FINAL",
    "PANEL BISNIS OK",
    "PANEL BISNIS NOTE",
    "SIAP PANEL BISNIS",
    "RAB",
    "LAYOUT HO",
    "LAYOUT CABANG",
    "UKUR",
    "OTS LOCAM OK",
    "BELUM OTS LOCAM",
    "SPTILOK",
    "SATILOK",
    "ULOK OTS LOCMAN",
    "ULOK FINDER"
]


# ==========================================================
# DISTRIBUSI PROGRESS
# ==========================================================

def get_progress_distribution(df, tahapan):

    df_tahap = df[
        df["TAHAPAN"].astype(str).str.strip().str.upper()
        == str(tahapan).strip().upper()
    ].copy()

    if df_tahap.empty:
        return {}

    distribution = (
        df_tahap["TAHAPAN 2"]
        .dropna()
        .astype(str)
        .str.strip()
    )

    distribution = (
        distribution[
            distribution != ""
        ]
        .str.upper()
        .value_counts()
        .to_dict()
    )

    return distribution


# ==========================================================
# DISTRIBUSI CABANG
# ==========================================================

def get_branch_distribution(
    df,
    tahapan,
    progress
):

    # ------------------------------------------------------
    # FILTER TAHAPAN
    # ------------------------------------------------------

    df_tahap = df[
        df["TAHAPAN"].astype(str).str.strip().str.upper()
        == str(tahapan).strip().upper()
    ].copy()

    if df_tahap.empty:
        return {}

    # ------------------------------------------------------
    # FILTER PROGRESS
    # ------------------------------------------------------

    progress_key = (
        str(progress)
        .strip()
        .upper()
    )

    df_progress = df_tahap[
        df_tahap["TAHAPAN 2"]
        .astype(str)
        .str.strip()
        .str.upper()
        == progress_key
    ].copy()

    if df_progress.empty:
        return {}

    # ------------------------------------------------------
    # HITUNG CABANG
    # ------------------------------------------------------

    branch_distribution = (
        df_progress["CAB"]
        .dropna()
        .astype(str)
        .str.strip()
    )

    branch_distribution = (
        branch_distribution[
            branch_distribution != ""
        ]
        .value_counts()
        .to_dict()
    )

    return branch_distribution


# ==========================================================
# INFO PROGRESS
# ==========================================================

def show_progress_info(
    df,
    tahapan
):

    distribution = get_progress_distribution(
        df,
        tahapan
    )

    state_key = (
        f"selected_progress_tahap_{tahapan}"
    )

    with st.popover(""):

        st.markdown(
            f"**Detail Progress TAHAP {tahapan}**"
        )

        if not distribution:

            st.caption(
                f"Tidak ada detail progress untuk TAHAP {tahapan}"
            )

            return

        # ==================================================
        # PROGRESS SESUAI URUTAN MAPPING
        # ==================================================

        for progress in PROGRESS_ORDER:

            progress_key = (
                str(progress)
                .strip()
                .upper()
            )

            if progress_key not in distribution:
                continue

            count = distribution[
                progress_key
            ]

            # --------------------------------------------------
            # TOMBOL PROGRESS
            # --------------------------------------------------

            if st.button(
                f"{progress}  —  {count:,}",
                key=(
                    f"progress_"
                    f"{tahapan}_"
                    f"{progress_key}"
                ),
                use_container_width=True
            ):

                # Jika progress yang sama diklik lagi,
                # tutup detailnya.
                if (
                    st.session_state.get(
                        state_key
                    )
                    == progress_key
                ):

                    st.session_state.pop(
                        state_key,
                        None
                    )

                # Jika progress berbeda diklik,
                # buka detail progress tersebut.
                else:

                    st.session_state[
                        state_key
                    ] = progress_key

                st.rerun()

            # ==================================================
            # DETAIL CABANG LANGSUNG DI BAWAH PROGRES
            # ==================================================

            selected_progress = (
                st.session_state.get(
                    state_key,
                    None
                )
            )

            if selected_progress == progress_key:

                branch_distribution = (
                    get_branch_distribution(
                        df,
                        tahapan,
                        selected_progress
                    )
                )

                if not branch_distribution:

                    st.caption(
                        "Tidak ada data CABANG."
                    )

                else:

                    total = 0

                    for (
                        branch,
                        branch_count
                    ) in branch_distribution.items():

                        st.markdown(
                            f"**{branch}** — "
                            f"{branch_count:,}"
                        )

                        total += branch_count

                    st.divider()

                    st.markdown(
                        f"**TOTAL — {total:,}**"
                    )


# ==========================================================
# KPI
# ==========================================================

def show_kpi(df):

    # ======================================================
    # HITUNG KPI
    # ======================================================

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

    # ======================================================
    # KPI
    # ======================================================

    col1, col2, col3, col4 = st.columns(4)

    # ======================================================
    # TOTAL PROPOSAL
    # ======================================================

    with col1:

        if st.button(
            f"📋 TOTAL PROPOSAL\n\n"
            f"{total_proposal:,}",
            use_container_width=True,
            key="kpi_total"
        ):

            st.session_state[
                "kpi_filter"
            ] = None

    # ======================================================
    # TAHAP 1
    # ======================================================

    with col2:

        kpi_col, info_col = st.columns(
            [8, 1]
        )

        with kpi_col:

            if st.button(
                f"🟡 TAHAP 1\n\n"
                f"{total_tahap1:,}",
                use_container_width=True,
                key="kpi_tahap1"
            ):

                st.session_state[
                    "kpi_filter"
                ] = "1"

        with info_col:

            show_progress_info(
                df,
                "1"
            )

    # ======================================================
    # TAHAP 2
    # ======================================================

    with col3:

        kpi_col, info_col = st.columns(
            [8, 1]
        )

        with kpi_col:

            if st.button(
                f"🟢 TAHAP 2\n\n"
                f"{total_tahap2:,}",
                use_container_width=True,
                key="kpi_tahap2"
            ):

                st.session_state[
                    "kpi_filter"
                ] = "2"

        with info_col:

            show_progress_info(
                df,
                "2"
            )

    # ======================================================
    # GO
    # ======================================================

    with col4:

        if st.button(
            f"🔵 GO\n\n"
            f"{total_go:,}",
            use_container_width=True,
            key="kpi_go"
        ):

            st.session_state[
                "kpi_filter"
            ] = "GO"

    # ======================================================
    # RETURN FILTER
    # ======================================================

    return st.session_state.get(
        "kpi_filter",
        None
    )