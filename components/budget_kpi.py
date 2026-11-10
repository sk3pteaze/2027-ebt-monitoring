
import streamlit as st
import pandas as pd

from data.loader import (
    load_progress_locam_new,
    load_data
)


# ==========================================================
# BULAN
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
# NORMALIZE
# ==========================================================

def normalize(value):

    if value is None:
        return ""

    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):
        pass

    return str(value).strip().upper()


# ==========================================================
# KONVERSI ANGKA
# ==========================================================

def to_number(value):

    if value is None:
        return 0

    if isinstance(value, (int, float)):
        return float(value)

    value = normalize(value)

    if value in ["", "-", "NAN", "NONE"]:
        return 0

    try:
        return float(value.replace(",", "."))
    except (ValueError, TypeError):
        return 0


# ==========================================================
# CEK FILTER KOSONG / SEMUA
# ==========================================================

def is_all(value):

    value = normalize(value)

    return value in [
        "",
        "SEMUA",
        "ALL",
        "NONE",
        "NAN",
        "RLM",
        "LOCAM",
        "CABANG"
    ]


# ==========================================================
# LOAD MASTER HIERARCHY
#
# Kolom master:
# RLM
# LOCAM
# CAB
#
# ==========================================================

@st.cache_data(ttl=300)
def load_hierarchy():

    df = load_data()

    if df is None or df.empty:
        return None

    # Hilangkan kolom duplikat
    df = df.loc[
        :,
        ~pd.Index(df.columns).duplicated()
    ].copy()

    # Normalisasi nama kolom
    df.columns = [
        normalize(column)
        for column in df.columns
    ]

    # Cari kolom LOCAM
    if "LOCAM" in df.columns:
        locam_column = "LOCAM"
    elif "LOCAM BARU" in df.columns:
        locam_column = "LOCAM BARU"
    else:
        return None

    required = [
        "RLM",
        locam_column,
        "CAB"
    ]

    for column in required:
        if column not in df.columns:
            return None

    temp = df[required].copy()

    temp.columns = [
        "RLM",
        "LOCAM",
        "CAB"
    ]

    for column in ["RLM", "LOCAM", "CAB"]:
        temp[column] = temp[column].apply(normalize)

    temp = temp[
        (temp["RLM"] != "")
        & (temp["LOCAM"] != "")
        & (temp["CAB"] != "")
    ].copy()

    return temp.drop_duplicates()


# ==========================================================
# CARI BLOK LOCAM
#
# Struktur:
#
# block_row      = NAMA LOCAM
# block_row + 1  = R
# block_row + 2  = TAHUN
# block_row + 3  = HEADER BULAN DAN CABANG
#
# Blok:
# 0, 44, 88, 132, 176, dst.
#
# ==========================================================

def find_blocks(df):

    blocks = []

    if df is None or df.empty:
        return blocks

    for block_row in range(0, len(df), 44):

        locam = normalize(
            df.iloc[block_row, 0]
        )

        if locam in ["", "NAN", "NONE"]:
            continue

        blocks.append({
            "block_row": block_row,
            "locam_row": block_row,
            "locam": locam
        })

    return blocks


# ==========================================================
# CARI KOLOM AWAL BULAN
#
# PENTING:
# Header bulan dicari di block_row,
# BUKAN block_row + 3.
#
# ==========================================================

def find_month_start_column(
    df,
    block_row,
    month
):

    month = normalize(month)

    for col_index in range(df.shape[1]):

        value = normalize(
            df.iloc[block_row, col_index]
        )

        if value == month:

            if col_index == 0:
                return col_index

            previous_value = normalize(
                df.iloc[block_row, col_index - 1]
            )

            if previous_value != month:
                return col_index

    return None


# ==========================================================
# CARI AKHIR KOLOM BULAN
# ==========================================================

def find_month_end_column(
    df,
    block_row,
    month_start_col,
    month
):

    for col_index in range(
        month_start_col + 1,
        df.shape[1]
    ):

        value = normalize(
            df.iloc[block_row, col_index]
        )

        if value == normalize(month):
            continue

        if value in MONTHS:
            return col_index - 1

    return df.shape[1] - 1


# ==========================================================
# CARI KOLOM CABANG
#
# Header cabang berada di:
# block_row + 3
#
# Header bulan berada di:
# block_row
#
# ==========================================================

def find_branch_column(
    df,
    block_row,
    month,
    branch
):

    # Cari bulan pada baris nama LOCAM
    month_start = find_month_start_column(
        df,
        block_row,
        month
    )

    if month_start is None:
        return None

    month_end = find_month_end_column(
        df,
        block_row,
        month_start,
        month
    )

    # Baris header cabang
    branch_row = block_row + 3

    if branch_row >= len(df):
        return None

    branch = normalize(branch)

    if is_all(branch):
        branch = "TOTAL"

    # Cari cabang dalam kelompok bulan
    for col_index in range(
        month_start,
        month_end + 1
    ):

        value = normalize(
            df.iloc[branch_row, col_index]
        )

        if value == branch:
            return col_index

    return None


# ==========================================================
# POSISI METRIC
#
# block + 4  = BUDGET GROSS
# block + 6  = BUDGET NET
# block + 11 = GO
#
# ==========================================================

METRIC_OFFSETS = {
    "BUDGET GROSS": 4,
    "BUDGET NET": 6,
    "GO": 11
}


# ==========================================================
# AMBIL NILAI SATU BLOK
# ==========================================================

def get_block_metric_value(
    df,
    block_row,
    month,
    branch,
    metric
):

    branch_col = find_branch_column(
        df,
        block_row,
        month,
        branch
    )

    if branch_col is None:
        return 0

    metric = normalize(metric)

    offset = METRIC_OFFSETS.get(metric)

    if offset is None:
        return 0

    metric_row = block_row + offset

    if metric_row >= len(df):
        return 0

    value = df.iloc[
        metric_row,
        branch_col
    ]

    return to_number(value)


# ==========================================================
# FILTER BLOK BERDASARKAN:
# RLM
# LOCAM
# CABANG
# ==========================================================

def get_allowed_blocks(
    df_progress,
    rlm=None,
    locam=None,
    branch=None
):

    blocks = find_blocks(df_progress)

    if not blocks:
        return []

    master = load_hierarchy()

    if master is None or master.empty:

        st.warning(
            "Master hierarchy tidak berhasil dibaca. "
            "Periksa kolom RLM, LOCAM, dan CAB."
        )

        return []

    rlm = normalize(rlm)
    locam = normalize(locam)
    branch = normalize(branch)

    # Filter RLM
    if not is_all(rlm):

        master = master[
            master["RLM"] == rlm
        ]

    # Filter LOCAM
    if not is_all(locam):

        master = master[
            master["LOCAM"] == locam
        ]

    # Filter cabang
    if not is_all(branch):

        master = master[
            master["CAB"] == branch
        ]

    allowed_locam = set(
        master["LOCAM"].unique()
    )

    result = []

    for block in blocks:

        block_locam = normalize(
            block["locam"]
        )

        if block_locam in allowed_locam:
            result.append(block)

    return result


# ==========================================================
# HITUNG NILAI SATU BULAN
# ==========================================================

def calculate_month(
    df,
    blocks,
    month,
    branch,
    metric
):

    total = 0

    # Jika cabang tertentu dipilih
    if not is_all(branch):

        selected_branch = normalize(branch)

        for block in blocks:

            total += get_block_metric_value(
                df,
                block["block_row"],
                month,
                selected_branch,
                metric
            )

        return total

    # Jika semua cabang:
    # Ambil kolom TOTAL setiap LOCAM

    for block in blocks:

        total += get_block_metric_value(
            df,
            block["block_row"],
            month,
            "TOTAL",
            metric
        )

    return total


# ==========================================================
# HITUNG KPI
# ==========================================================

def calculate_kpi(
    df,
    month,
    rlm=None,
    locam=None,
    branch=None
):

    current_month = normalize(month)

    if current_month not in MONTHS:

        raise ValueError(
            f"Bulan KPI tidak valid: {month}"
        )

    current_month_number = (
        MONTHS.index(current_month) + 1
    )

    # Filter blok LOCAM
    blocks = get_allowed_blocks(
        df,
        rlm=rlm,
        locam=locam,
        branch=branch
    )

    metrics = [
        "BUDGET GROSS",
        "BUDGET NET",
        "GO"
    ]

    # ======================================================
    # BULAN BERJALAN
    # ======================================================

    current = {}

    for metric in metrics:

        current[metric] = calculate_month(
            df,
            blocks,
            current_month,
            branch,
            metric
        )

    # ======================================================
    # YTD: JANUARI - BULAN TERPILIH
    # ======================================================

    ytd = {}

    months_ytd = MONTHS[
        :current_month_number
    ]

    for metric in metrics:

        ytd[metric] = sum(
            calculate_month(
                df,
                blocks,
                month_name,
                branch,
                metric
            )
            for month_name in months_ytd
        )

    # ======================================================
    # YEARLY: JANUARI - DESEMBER
    # ======================================================

    yearly = {}

    for metric in metrics:

        yearly[metric] = sum(
            calculate_month(
                df,
                blocks,
                month_name,
                branch,
                metric
            )
            for month_name in MONTHS
        )

    return (
        current_month,
        current,
        ytd,
        yearly
    )


# ==========================================================
# DISPLAY KPI
# ==========================================================

def show_budget_kpi(
    month,
    rlm=None,
    locam=None,
    branch=None
):

    df = load_progress_locam_new()

    if df is None or df.empty:

        st.info(
            "Data PROGRESS LOCAM NEW belum tersedia."
        )

        return

    (
        current_month,
        current,
        ytd,
        yearly
    ) = calculate_kpi(
        df,
        month=month,
        rlm=rlm,
        locam=locam,
        branch=branch
    )

    st.markdown(
        f"### Budget & GO — {current_month.title()}"
    )

    cols = st.columns(3)

    metrics = [
        (
            "BUDGET GROSS",
            current["BUDGET GROSS"],
            ytd["BUDGET GROSS"],
            yearly["BUDGET GROSS"]
        ),
        (
            "BUDGET NET",
            current["BUDGET NET"],
            ytd["BUDGET NET"],
            yearly["BUDGET NET"]
        ),
        (
            "GO",
            current["GO"],
            ytd["GO"],
            yearly["GO"]
        )
    ]

    for col, (
        title,
        current_value,
        ytd_value,
        yearly_value
    ) in zip(cols, metrics):

        with col:

            st.metric(
                label=title,
                value=f"{current_value:g}"
            )

            st.caption(
                f"Jan–{current_month[:3].title()}: "
                f"{ytd_value:g} • "
                f"Jan–Des: {yearly_value:g}"
            )
