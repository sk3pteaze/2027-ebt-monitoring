
import streamlit as st
import pandas as pd

from datetime import datetime

from config import COLUMN

from data.loader import load_data
from components.filters import progress_filters
from components.apply_filters import apply_filters
from components.kpi import show_kpi
from components.progress_timeline import show_progress_timeline
from components.weekly_comparison import (
    show_comparison_picker,
)
from components.progress_budget_chart import (
    show_progress_budget_chart
)
from components.budget_kpi import show_budget_kpi


# ==========================================================
# RESET SAAT PROPOSAL DI-CLEAR
# ==========================================================

def reset_proposal_state():

    # ------------------------------------------------------
    # Naikkan version tabel
    # ------------------------------------------------------

    st.session_state[
        "proposal_table_version"
    ] = (
        st.session_state.get(
            "proposal_table_version",
            0
        )
        + 1
    )

    # ------------------------------------------------------
    # Naikkan version snapshot
    # ------------------------------------------------------

    st.session_state[
        "snapshot_reset_version"
    ] = (
        st.session_state.get(
            "snapshot_reset_version",
            0
        )
        + 1
    )


# ==========================================================
# TAB 1
# ==========================================================

def tab_1():

    # ======================================================
    # INIT STATE
    # ======================================================

    if "proposal_table_version" not in st.session_state:

        st.session_state[
            "proposal_table_version"
        ] = 0

    if "snapshot_reset_version" not in st.session_state:

        st.session_state[
            "snapshot_reset_version"
        ] = 0


    # ======================================================
    # COLUMN CONFIG
    # ======================================================

    proposal_col = COLUMN["proposal"]
    progress_col = COLUMN["progress"]
    tahapan_col = COLUMN["tahapan"]
    bulan_go_col = COLUMN["bulan_go"]
    progress_proposal_col = COLUMN["progress_proposal"]


    # ======================================================
    # LOAD DATA
    # ======================================================

    df = load_data()

    if df.empty:

        st.warning("Data master tidak ditemukan.")

        return


    # ======================================================
    # VALIDASI KOLOM
    # ======================================================

    required_columns = [
        proposal_col,
        progress_col,
        tahapan_col,
        bulan_go_col,
        progress_proposal_col,
        "KOORDINAT LOKASI",
        "TGL ESTIMASI GO"
    ]

    missing_columns = [
        col
        for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:

        st.error(
            "Kolom berikut tidak ditemukan di MASTER:\n"
            + ", ".join(missing_columns)
        )

        st.caption(
            f"Kolom tersedia: {df.columns.tolist()}"
        )

        return


    # ======================================================
    # FILTER
    # ======================================================

    filters = progress_filters(df)

    df_filtered = apply_filters(
        df,
        filters
    )


    # ======================================================
    # KPI
    # ======================================================

    kpi_filter = show_kpi(
        df_filtered
    )


    # ======================================================
    # APPLY KPI FILTER
    # ======================================================

    if kpi_filter is not None:

        df_filtered = df_filtered[
            df_filtered[tahapan_col].astype(str)
            ==
            str(kpi_filter)
        ].copy()


    # ======================================================
    # BUDGET VS ESTIMASI BUDGET
    # ======================================================

    # show_progress_budget_chart(
    #     df_filtered,
    #     filters.get("sm")
    # )

    # st.divider()


    # ======================================================
    # BUDGET KPI
    # ======================================================

    selected_bulan_kpi = filters.get("bulan_kpi")
    selected_rlm = filters.get("rlm")
    selected_locam = filters.get("locam")
    selected_branch = filters.get("cabang")

    show_budget_kpi(
        month=selected_bulan_kpi,
        rlm=selected_rlm,
        locam=selected_locam,
        branch=selected_branch
    )

    st.divider()


    # ======================================================
    # SELECTBOX PROPOSAL
    # ======================================================

    proposal_options = sorted(
        df_filtered[
            proposal_col
        ]
        .dropna()
        .astype(str)
        .str.strip()
        .loc[lambda x: x != ""]
        .unique()
        .tolist()
    )


    selected_from_box = st.selectbox(

        "Pilih Proposal",

        options=proposal_options,

        index=None,

        placeholder=(
            "Ketik atau pilih nama proposal..."
        ),

        key="proposal_selector",

        on_change=reset_proposal_state
    )


    # ======================================================
    # FILTER TABEL BERDASARKAN SELECTBOX
    # ======================================================

    if selected_from_box:

        df_table = df_filtered[
            df_filtered[
                proposal_col
            ]
            .astype(str)
            .str.strip()
            ==
            str(selected_from_box).strip()
        ].copy()

    else:

        df_table = df_filtered.copy()


    # ======================================================
    # TABEL PROPOSAL
    # ======================================================

    proposal_table = df_table[

        [
            proposal_col,
            "CAB",
            "KOORDINAT LOKASI",
            "TGL ESTIMASI GO",
            bulan_go_col,
            progress_col,
            progress_proposal_col
        ]

    ].copy()


    # ======================================================
    # RENAME KOLOM UNTUK TAMPILAN
    # ======================================================

    proposal_table = proposal_table.rename(

        columns={

            proposal_col: "NAMA PROPOSAL",

            progress_col: "TAHAPAN"

        }

    )


    # ======================================================
    # SORT BULAN GO
    # ======================================================

    bulan_order = {

        "JANUARI": 1,
        "FEBRUARI": 2,
        "MARET": 3,
        "APRIL": 4,
        "MEI": 5,
        "JUNI": 6,
        "JULI": 7,
        "AGUSTUS": 8,
        "SEPTEMBER": 9,
        "OKTOBER": 10,
        "NOVEMBER": 11,
        "DESEMBER": 12

    }


    proposal_table["_bulan_order"] = (

        proposal_table[bulan_go_col]

        .astype(str)

        .str.strip()

        .str.upper()

        .map(bulan_order)

    )


    # ======================================================
    # SORT TGL ESTIMASI GO
    # ======================================================

    proposal_table["_tgl_go_sort"] = pd.to_datetime(

        proposal_table[
            "TGL ESTIMASI GO"
        ],

        errors="coerce"

    )


    proposal_table = (

        proposal_table

        .sort_values(

            by=[
                "_bulan_order",
                "_tgl_go_sort"
            ],

            ascending=[
                True,
                True
            ],

            na_position="last"

        )

        .drop(

            columns=[
                "_bulan_order",
                "_tgl_go_sort"
            ]

        )

        .reset_index(
            drop=True
        )

    )


    # ======================================================
    # HEADER
    # ======================================================

    st.markdown(
        "### 📋 Daftar Proposal"
    )


    if selected_from_box:

        st.caption(
            f"Proposal yang ditampilkan: **{selected_from_box}**"
        )

    else:

        st.caption(
            "Proposal yang ditampilkan: "
            "**Semua Proposal**"
        )


    # ======================================================
    # DATAFRAME
    # ======================================================

    proposal_table_key = (

        f"proposal_table_"

        f"{st.session_state['proposal_table_version']}"

    )


    proposal_event = st.dataframe(

        proposal_table,

        use_container_width=True,

        hide_index=True,

        selection_mode="single-row",

        on_select="rerun",

        key=proposal_table_key

    )


    # ======================================================
    # PROPOSAL YANG DIKLIK DI TABEL
    # ======================================================

    clicked_proposal = None

    selected_rows = (
        proposal_event.selection.rows
    )


    if selected_rows:

        selected_index = selected_rows[0]

        clicked_proposal = (

            proposal_table.iloc[
                selected_index
            ][
                "NAMA PROPOSAL"
            ]

        )


    # ======================================================
    # SNAPSHOT COMPARISON
    #
    # reset_version berubah ketika selectbox proposal
    # di-clear.
    #
    # Date picker kembali ke default.
    # ======================================================

    show_comparison_picker(

        reset_token=(

            st.session_state[
                "snapshot_reset_version"
            ]

        )

    )


    # ======================================================
    # DETAIL / TIMELINE
    #
    # TIMELINE HANYA MUNCUL JIKA ROW TABEL DIKLIK
    # ======================================================

    if clicked_proposal is not None:

        selected_rows_df = df_filtered[

            df_filtered[
                proposal_col
            ]

            .astype(str)

            .str.strip()

            ==

            str(clicked_proposal).strip()

        ].copy()


        if not selected_rows_df.empty:

            selected_row = (
                selected_rows_df.iloc[0]
            )


            # ==================================================
            # TIMELINE
            # ==================================================

            show_progress_timeline(

                selected_row,

                clicked_proposal

            )
