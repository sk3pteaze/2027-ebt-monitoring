import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from data.loader import load_progress_sm


# ==========================================================
# URUTAN BULAN
# ==========================================================

MONTHS = [
    "JANUARI",
    "FEBRUARI",
    "MARET",
    "APRIL",
    "MEI",
    "JUNI",
    "JULI",
    "AGUSTUS",
    "SEPTEMBER",
    "OKTOBER",
    "NOVEMBER",
    "DESEMBER"
]


# ==========================================================
# ALIAS BULAN
# ==========================================================

MONTH_ALIASES = {
    "JAN": "JANUARI",
    "JANUARI": "JANUARI",

    "FEB": "FEBRUARI",
    "FEBRUARI": "FEBRUARI",

    "MAR": "MARET",
    "MARET": "MARET",

    "APR": "APRIL",
    "APRIL": "APRIL",

    "MEI": "MEI",

    "JUN": "JUNI",
    "JUNI": "JUNI",

    "JUL": "JULI",
    "JULI": "JULI",

    "AGU": "AGUSTUS",
    "AGUSTUS": "AGUSTUS",

    "SEP": "SEPTEMBER",
    "SEPTEMBER": "SEPTEMBER",

    "OKT": "OKTOBER",
    "OKTOBER": "OKTOBER",

    "NOV": "NOVEMBER",
    "NOVEMBER": "NOVEMBER",

    "DES": "DESEMBER",
    "DESEMBER": "DESEMBER"
}


# ==========================================================
# CARI BARIS BUDGET GROSS
# ==========================================================

def find_budget_row(
    df,
    selected_sm=None
):

    if df.empty:
        return None

    selected_sm = (
        str(selected_sm)
        .strip()
        .upper()
        if selected_sm
        else None
    )

    # ------------------------------------------------------
    # Jika SM dipilih, cari posisi SM terlebih dahulu
    # ------------------------------------------------------

    start_search = 0

    if selected_sm:

        for i in range(len(df)):

            row_text = " ".join(
                df.iloc[i]
                .astype(str)
                .str.strip()
                .str.upper()
                .tolist()
            )

            if selected_sm in row_text:

                start_search = i
                break

    # ------------------------------------------------------
    # Cari BUDGET GROSS
    # ------------------------------------------------------

    for i in range(
        start_search,
        len(df)
    ):

        row_text = " ".join(
            df.iloc[i]
            .astype(str)
            .str.strip()
            .str.upper()
            .tolist()
        )

        if "BUDGET GROSS" in row_text:

            return i

    # ------------------------------------------------------
    # Fallback
    # ------------------------------------------------------

    for i in range(len(df)):

        row_text = " ".join(
            df.iloc[i]
            .astype(str)
            .str.strip()
            .str.upper()
            .tolist()
        )

        if "BUDGET GROSS" in row_text:

            return i

    return None


# ==========================================================
# CARI KOLOM BULAN
# ==========================================================

def find_month_columns(
    df,
    budget_row_index
):

    month_columns = {}

    start = max(
        0,
        budget_row_index - 5
    )

    end = min(
        len(df),
        budget_row_index + 1
    )

    for row_index in range(
        start,
        end
    ):

        for col_index in range(
            df.shape[1]
        ):

            value = (
                str(
                    df.iloc[
                        row_index,
                        col_index
                    ]
                )
                .strip()
                .upper()
            )

            if value in MONTH_ALIASES:

                month = MONTH_ALIASES[
                    value
                ]

                month_columns[
                    month
                ] = col_index

    return month_columns


# ==========================================================
# AMBIL BUDGET GROSS
# ==========================================================

def get_budget_gross(
    progress_sm_df,
    selected_sm=None
):

    result = pd.Series(
        0.0,
        index=MONTHS
    )

    if progress_sm_df.empty:

        return result

    budget_row_index = find_budget_row(
        progress_sm_df,
        selected_sm
    )

    if budget_row_index is None:

        return result

    month_columns = find_month_columns(
        progress_sm_df,
        budget_row_index
    )

    budget_row = progress_sm_df.iloc[
        budget_row_index
    ]

    for month in MONTHS:

        if month not in month_columns:

            continue

        col_index = month_columns[
            month
        ]

        value = budget_row.iloc[
            col_index
        ]

        try:

            value = (
                str(value)
                .strip()
                .replace(",", "")
                .replace(".", "")
            )

            result.loc[month] = float(
                value
            )

        except (
            ValueError,
            TypeError
        ):

            result.loc[month] = 0

    return result


# ==========================================================
# ESTIMASI BUDGET
# ==========================================================

def get_estimated_budget(
    df_filtered
):

    result = pd.Series(
        0.0,
        index=MONTHS
    )

    if df_filtered.empty:

        return result

    df = df_filtered.copy()

    # ------------------------------------------------------
    # Pastikan kolom tersedia
    # ------------------------------------------------------

    if "TAHAPAN 2" not in df.columns:
        return result

    if "BULAN GO" not in df.columns:
        return result

    # ------------------------------------------------------
    # Hanya proposal yang memiliki TAHAPAN 2
    # ------------------------------------------------------

    tahapan_2 = (
        df["TAHAPAN 2"]
        .astype(str)
        .str.strip()
    )

    df = df[
        (tahapan_2 != "")
        &
        (tahapan_2.str.upper() != "NAN")
    ].copy()

    if df.empty:

        return result

    # ------------------------------------------------------
    # Normalisasi BULAN GO
    # ------------------------------------------------------

    df["_bulan_go"] = (
        df["BULAN GO"]
        .astype(str)
        .str.strip()
        .str.upper()
        .map(MONTH_ALIASES)
    )

    # ------------------------------------------------------
    # Hitung proposal per bulan
    # ------------------------------------------------------

    counts = (
        df["_bulan_go"]
        .value_counts()
    )

    for month in MONTHS:

        result.loc[month] = counts.get(
            month,
            0
        )

    return result


# ==========================================================
# CHART
# ==========================================================

def show_progress_budget_chart(
    df_filtered,
    selected_sm=None
):

    st.markdown(
        "### 📊 Budget vs Estimasi Budget"
    )

    # ======================================================
    # LOAD PROGRESS SM
    # ======================================================

    progress_sm_df = load_progress_sm()

    if progress_sm_df.empty:

        st.info(
            "Data PROGRESS SM belum tersedia."
        )

        return

    # ======================================================
    # BUDGET
    # ======================================================

    budget = get_budget_gross(
        progress_sm_df,
        selected_sm
    )

    # ======================================================
    # ESTIMASI BUDGET
    # ======================================================

    estimated_budget = (
        get_estimated_budget(
            df_filtered
        )
    )

    # ======================================================
    # DATA CHART
    # ======================================================

    chart_df = pd.DataFrame({
        "BULAN": MONTHS,
        "Budget": budget.reindex(
            MONTHS
        ).values,
        "Estimasi Budget": (
            estimated_budget
            .reindex(MONTHS)
            .values
        )
    })

    # ======================================================
    # PLOTLY
    # ======================================================

    fig = go.Figure()

    # ------------------------------------------------------
    # BAR BUDGET
    # ------------------------------------------------------

    fig.add_trace(
        go.Bar(
            x=chart_df["BULAN"],
            y=chart_df["Budget"],
            name="Budget"
        )
    )

    # ------------------------------------------------------
    # BAR ESTIMASI BUDGET
    # ------------------------------------------------------

    fig.add_trace(
        go.Bar(
            x=chart_df["BULAN"],
            y=chart_df["Estimasi Budget"],
            name="Estimasi Budget"
        )
    )

    # ======================================================
    # LAYOUT
    # ======================================================

    fig.update_layout(
        barmode="group",

        height=400,

        margin=dict(
            l=20,
            r=20,
            t=10,
            b=20
        ),

        plot_bgcolor="rgba(0,0,0,0)",

        paper_bgcolor="rgba(0,0,0,0)",

        hovermode="x unified",

        dragmode=False,

        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    # ======================================================
    # X AXIS
    # ======================================================

    fig.update_xaxes(
        fixedrange=True,

        categoryorder="array",

        categoryarray=MONTHS,

        showgrid=False
    )

    # ======================================================
    # Y AXIS
    # ======================================================

    fig.update_yaxes(
        fixedrange=True,

        rangemode="tozero",

        showgrid=True
    )

    # ======================================================
    # DISPLAY
    # ======================================================

    st.plotly_chart(
        fig,

        use_container_width=True,

        config={
            "displayModeBar": False,
            "scrollZoom": False,
            "doubleClick": False,
            "displaylogo": False
        }
    )