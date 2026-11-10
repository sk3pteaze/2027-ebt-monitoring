import streamlit as st
import pandas as pd

from data.loader import load_progress_locam_new
from components.budget_kpi import (
    get_allowed_blocks,
    calculate_month,
)


# ==========================================================
# MASTER PROGRESS -> TAHAPAN MAPPING
# ==========================================================

PROGRESS_MAPPING = {
    "GO": "GO",

    # TAHAP 2
    "SERAH TERIMA PROJECT": "2",
    "RENOVASI": "2",
    "NOTARIS": "2",
    "RENCANA NOTARIS": "2",
    "IZIN": "2",
    "PROPOSAL ACC": "2",

    # TAHAP 1
    "PROP HO - DIREKSI": "1",
    "PROP HO - AUDIT": "1",
    "PROP HO - LOC": "1",
    "PANEL FINAL OK": "1",
    "PANEL FINAL NOTE": "1",
    "SIAP PANEL FINAL": "1",
    "PANEL BISNIS OK": "1",
    "PANEL BISNIS NOTE": "1",
    "SIAP PANEL BISNIS": "1",
    "RAB": "1",
    "LAYOUT HO": "1",
    "LAYOUT CABANG": "1",
    "UKUR": "1",
    "OTS LOCAM OK": "1",
    "BELUM OTS LOCAM": "1",
    "SPTILOK": "1",
    "SATILOK": "1",
    "ULOK OTS LOCMAN": "1",
    "ULOK FINDER": "1",
}


# ==========================================================
# URUTAN PROGRESS
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
    "ULOK FINDER",
]


TAHAP2_ORDER = [
    progress
    for progress in PROGRESS_ORDER
    if PROGRESS_MAPPING.get(progress) == "2"
]


TAHAP1_ORDER = [
    progress
    for progress in PROGRESS_ORDER
    if PROGRESS_MAPPING.get(progress) == "1"
]


# ==========================================================
# HELPER
# ==========================================================

def normalize(value):
    return str(value).strip().upper()


def format_number(value):
    if pd.isna(value):
        return "0"

    try:
        value = float(value)

        if value.is_integer():
            return f"{int(value):,}"

        return f"{value:,.1f}"

    except (ValueError, TypeError):
        return value


def style_negative_red(styler):
    """
    Semua angka negatif diberi warna merah.
    Nilai tetap ditampilkan sebagai angka negatif,
    contoh: -112
    """

    def color_negative(value):
        try:
            if pd.notna(value) and float(value) < 0:
                return "color: red; font-weight: 700;"
        except (ValueError, TypeError):
            pass

        return ""

    numeric_columns = styler.data.select_dtypes(
        include=["number"]
    ).columns

    return styler.map(
        color_negative,
        subset=numeric_columns
    )


def style_table_header(styler):
    """
    Header Tabel 1 dan Tabel 2 dibuat seragam.
    Background biru muda dan tulisan hitam.
    """
    return styler.set_table_styles([
        {
            "selector": "table",
            "props": [
                ("border-collapse", "collapse"),
                ("border", "1px solid #000000 !important"),
            ],
        },
        {
            "selector": "thead th, tbody td",
            "props": [
                ("border", "1px solid #000000 !important"),
            ],
        },
        {
            "selector": "thead th",
            "props": [
                ("background-color", "#E2F0D9 !important"),
                ("color", "#000000 !important"),
                ("font-weight", "700 !important"),
                ("text-align", "center !important"),
            ],
        },
        {
            "selector": "th.col_heading",
            "props": [
                ("background-color", "#E2F0D9 !important"),
                ("color", "#000000 !important"),
                ("font-weight", "700 !important"),
                ("text-align", "center !important"),
            ],
        },
        {
            "selector": "th.blank",
            "props": [
                ("background-color", "#E2F0D9 !important"),
            ],
        },
    ])


def format_dataframe(df):
    """
    Format angka tanpa mengubah nilai aslinya.
    """

    styler = df.style.format(
        lambda value: format_number(value)
        if isinstance(value, (int, float))
        else value
    )

    return style_negative_red(styler)


# ==========================================================
# BUILD DETAIL MATRIX
# ==========================================================

def build_progress_matrix(df):

    required_columns = [
        "RLM",
        "CAB",
        "TAHAPAN 2",
    ]

    missing = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing:
        st.error(
            "Kolom yang dibutuhkan tidak ditemukan: "
            + ", ".join(missing)
        )
        return pd.DataFrame()

    work = df.copy()

    # ------------------------------------------------------
    # RLM
    # ------------------------------------------------------
    work["_RLM"] = (
        work["RLM"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.upper()
    )

    # ------------------------------------------------------
    # CABANG
    # ------------------------------------------------------
    work["_CAB"] = (
        work["CAB"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.upper()
    )

    # ------------------------------------------------------
    # MASTER PROGRESS
    # ------------------------------------------------------
    work["_MASTER_PROGRESS"] = (
        work["TAHAPAN 2"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.upper()
    )

    work = work[
        (work["_CAB"] != "")
        & (work["_RLM"] != "")
    ].copy()

    if work.empty:
        return pd.DataFrame()

    # ------------------------------------------------------
    # APPLY MAPPING
    # ------------------------------------------------------
    work["_TAHAPAN_MAPPING"] = (
        work["_MASTER_PROGRESS"]
        .map(PROGRESS_MAPPING)
        .fillna("")
    )

    # ------------------------------------------------------
    # HIERARKI RLM -> CAB
    # ------------------------------------------------------
    # Satu CAB diasumsikan berada di bawah satu RLM.
    # Jika ada beberapa nilai RLM untuk CAB yang sama, nilai pertama
    # yang ditemukan dipakai sebagai mapping.
    cab_rlm_map = (
        work[["_CAB", "_RLM"]]
        .drop_duplicates(subset=["_CAB"])
        .set_index("_CAB")["_RLM"]
        .to_dict()
    )

    # Urutan RLM mengikuti urutan alfabet, kemudian CAB di dalam RLM
    # juga diurutkan alfabet. Ini membuat subtotal RLM berada setelah
    # seluruh CAB yang berada di bawahnya.
    rlm_by_cab = {}
    for cab, rlm in cab_rlm_map.items():
        rlm_by_cab.setdefault(rlm, []).append(cab)

    for rlm in rlm_by_cab:
        rlm_by_cab[rlm] = sorted(rlm_by_cab[rlm])

    ordered_rlms = sorted(rlm_by_cab.keys())
    branches = [
        cab
        for rlm in ordered_rlms
        for cab in rlm_by_cab[rlm]
    ]

    # Nama kolom subtotal RLM menggunakan nama RLM langsung.
    # Contoh: JABAR, JATENG.
    rlm_columns = {
        rlm: f"{rlm}"
        for rlm in ordered_rlms
    }

    display_columns = []
    for rlm in ordered_rlms:
        display_columns.extend(rlm_by_cab[rlm])
        display_columns.append(rlm_columns[rlm])

    result = []

    def add_progress_row(progress, tahap_mapping):
        row = {"PROGRESS": progress}

        for rlm in ordered_rlms:
            rlm_total = 0

            for branch in rlm_by_cab[rlm]:
                count = int(
                    (
                        (work["_CAB"] == branch)
                        & (work["_TAHAPAN_MAPPING"] == tahap_mapping)
                        & (work["_MASTER_PROGRESS"] == progress)
                    ).sum()
                )
                row[branch] = count
                rlm_total += count

            row[rlm_columns[rlm]] = rlm_total

        row["TOTAL"] = sum(
            row[rlm_columns[rlm]]
            for rlm in ordered_rlms
        )
        result.append(row)

    # ======================================================
    # TAHAP 2
    # ======================================================
    for progress in TAHAP2_ORDER:
        add_progress_row(progress, "2")

    # ------------------------------------------------------
    # TOTAL TAHAP 2
    # ------------------------------------------------------
    row = {"PROGRESS": "TOTAL TAHAP 2"}
    for rlm in ordered_rlms:
        rlm_total = 0
        for branch in rlm_by_cab[rlm]:
            count = int(
                (
                    (work["_CAB"] == branch)
                    & (work["_TAHAPAN_MAPPING"] == "2")
                ).sum()
            )
            row[branch] = count
            rlm_total += count
        row[rlm_columns[rlm]] = rlm_total
    row["TOTAL"] = sum(row[rlm_columns[rlm]] for rlm in ordered_rlms)
    result.append(row)

    # ======================================================
    # TAHAP 1
    # ======================================================
    for progress in TAHAP1_ORDER:
        add_progress_row(progress, "1")

    # ------------------------------------------------------
    # TOTAL TAHAP 1
    # ------------------------------------------------------
    row = {"PROGRESS": "TOTAL TAHAP 1"}
    for rlm in ordered_rlms:
        rlm_total = 0
        for branch in rlm_by_cab[rlm]:
            count = int(
                (
                    (work["_CAB"] == branch)
                    & (work["_TAHAPAN_MAPPING"] == "1")
                ).sum()
            )
            row[branch] = count
            rlm_total += count
        row[rlm_columns[rlm]] = rlm_total
    row["TOTAL"] = sum(row[rlm_columns[rlm]] for rlm in ordered_rlms)
    result.append(row)

    result = pd.DataFrame(result)

    # Metadata dipakai oleh Tabel 2/3 supaya kolom subtotal RLM tidak
    # dianggap sebagai CAB saat mengambil Budget & GO atau cumulative.
    result.attrs["branches"] = branches
    result.attrs["ordered_rlms"] = ordered_rlms
    result.attrs["rlm_by_cab"] = rlm_by_cab
    result.attrs["rlm_columns"] = rlm_columns
    result.attrs["display_columns"] = display_columns

    return result


# ==========================================================
# CALCULATE BUDGET & GO PER CABANG
# ==========================================================

@st.cache_data(ttl=300)
def calculate_branch_budget_go(branches):

    df_progress = load_progress_locam_new()

    if df_progress is None or df_progress.empty:
        return {}

    blocks = get_allowed_blocks(
        df_progress,
        rlm=None,
        locam=None,
        branch=None,
    )

    if not blocks:
        return {}

    result = {}

    months = [
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
        "DESEMBER",
    ]

    for branch in branches:

        budget_gross = 0
        go = 0

        for month in months:

            budget_gross += calculate_month(
                df_progress,
                blocks,
                month,
                branch,
                "BUDGET GROSS",
            )

            go += calculate_month(
                df_progress,
                blocks,
                month,
                branch,
                "GO",
            )

        result[normalize(branch)] = {
            "BUDGET GROSS": budget_gross,
            "GO": go,
        }

    return result


# ==========================================================
# CALCULATE OVERALL BUDGET & GO DARI KOLOM TOTAL
# ==========================================================

@st.cache_data(ttl=300)
def calculate_overall_budget_go():

    df_progress = load_progress_locam_new()

    if df_progress is None or df_progress.empty:
        return 0, 0

    # Gunakan filter hierarchy LOCAM yang sama dengan Budget KPI.
    # branch=None akan membuat calculate_month mengambil kolom TOTAL
    # pada setiap blok LOCAM.
    blocks = get_allowed_blocks(
        df_progress,
        rlm=None,
        locam=None,
        branch=None,
    )

    if not blocks:
        return 0, 0

    months = [
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
        "DESEMBER",
    ]

    total_budget = sum(
        calculate_month(
            df_progress,
            blocks,
            month,
            None,
            "BUDGET GROSS",
        )
        for month in months
    )

    total_go = sum(
        calculate_month(
            df_progress,
            blocks,
            month,
            None,
            "GO",
        )
        for month in months
    )

    return total_budget, total_go


# ==========================================================
# TABLE 1 - KPI SUMMARY
# ==========================================================

def show_kpi_summary(
    total_budget,
    total_go,
    total_tahap1,
    total_tahap2,
):

    total_proposal = (
        total_tahap1
        + total_tahap2
    )

    # Variance = GO - Budget Gross
    variance = total_go - total_budget

    summary = pd.DataFrame(
        [{
            "Budget Gross": total_budget,
            "GO": total_go,
            "Variance": variance,
            "": "",
            "Tahap 1": total_tahap1,
            "Tahap 2": total_tahap2,
            "TOTAL": total_proposal,
        }]
    )

    styler = summary.style.format({
        "Budget Gross": "{:,.0f}",
        "GO": "{:,.0f}",
        "Variance": "{:,.0f}",
        "Tahap 1": "{:,.0f}",
        "Tahap 2": "{:,.0f}",
        "TOTAL": "{:,.0f}",
    })

    # Hanya HEADER yang diberi warna.
    # Warna header sama dengan Tabel 2.
    styler = style_table_header(styler)

    # Nilai negatif tetap negatif dan berwarna merah.
    def negative_red(value):
        try:
            if pd.notna(value) and float(value) < 0:
                return "color: red; font-weight: 700;"
        except (ValueError, TypeError):
            pass
        return ""

    styler = styler.map(
        negative_red,
        subset=[
            "Budget Gross",
            "GO",
            "Variance",
            "Tahap 1",
            "Tahap 2",
            "TOTAL",
        ],
    )

    # Render sebagai HTML agar styling header dari Pandas Styler
    # benar-benar diterapkan. st.dataframe() dapat mengabaikan styling <th>.
    st.markdown(
        '<div class="responsive-matrix responsive-kpi">'
        + styler.hide(axis="index").to_html()
        + '</div>',
        unsafe_allow_html=True,
    )


# ==========================================================
# TABLE 2 - SUMMARY PER CABANG
# ==========================================================

def style_branch_summary(df, rlm_columns=None):
    """
    Styling Tabel 2:
    - Header sama dengan Tabel 1
    - Body tetap memakai warna kategori
    - Nilai negatif tetap merah
    """

    styler = df.style.format(
        lambda value: format_number(value)
        if isinstance(value, (int, float))
        else value
    )

    if "" in df.columns:
        row_colors = {
            "Target GO": "#E7E6E6",
            "Tahap 2": "#D9EAF7",
            "Tahap 1": "#FFF2CC",
            "TOTAL PROPOSAL": "#D9D9D9",
            "Variance": "#FFC7CE",
        }

        for label, color in row_colors.items():
            rows = df.index[df[""] == label].tolist()

            if rows:
                styler = styler.set_properties(
                    subset=pd.IndexSlice[rows[0], :],
                    **{
                        "background-color": color,
                        "font-weight": "700",
                    },
                )

    numeric_columns = df.select_dtypes(
        include=["number"]
    ).columns

    def negative_red(value):
        try:
            if pd.notna(value) and float(value) < 0:
                return "color: red; font-weight: 700;"
        except (ValueError, TypeError):
            pass
        return ""

    if len(numeric_columns) > 0:
        styler = styler.map(
            negative_red,
            subset=numeric_columns,
        )

    # Header Tabel 2 sama dengan header Tabel 1.
    styler = style_table_header(styler)

    # Header subtotal RLM diberi warna ungu.
    styler = style_rlm_headers(
        styler,
        df,
        rlm_columns=rlm_columns or {},
    )

    return styler


def build_branch_summary(
    branches,
    budget_go,
    matrix,
):

    ordered_rlms = matrix.attrs.get("ordered_rlms", [])
    rlm_by_cab = matrix.attrs.get("rlm_by_cab", {})
    rlm_columns = matrix.attrs.get("rlm_columns", {})
    display_columns = matrix.attrs.get("display_columns", branches)

    # ------------------------------------------------------
    # Ambil total Tahap 1
    # ------------------------------------------------------
    tahap1_row = matrix[
        matrix["PROGRESS"] == "TOTAL TAHAP 1"
    ]
    tahap1_row = tahap1_row.iloc[0] if not tahap1_row.empty else None

    # ------------------------------------------------------
    # Ambil total Tahap 2
    # ------------------------------------------------------
    tahap2_row = matrix[
        matrix["PROGRESS"] == "TOTAL TAHAP 2"
    ]
    tahap2_row = tahap2_row.iloc[0] if not tahap2_row.empty else None

    rows = []

    # ======================================================
    # TARGET GO
    # ======================================================
    row = {"": "Target GO"}

    for rlm in ordered_rlms:
        rlm_target = 0

        for branch in rlm_by_cab[rlm]:
            values = budget_go.get(
                normalize(branch),
                {"BUDGET GROSS": 0, "GO": 0},
            )
            target = max(
                values["BUDGET GROSS"] - values["GO"],
                0,
            )
            row[branch] = target
            rlm_target += target

        row[rlm_columns[rlm]] = rlm_target

    row["TOTAL"] = sum(row[rlm_columns[rlm]] for rlm in ordered_rlms)
    rows.append(row)

    # ======================================================
    # TAHAP 2
    # ======================================================
    row = {"": "Tahap 2"}
    for rlm in ordered_rlms:
        rlm_total = 0
        for branch in rlm_by_cab[rlm]:
            value = tahap2_row[branch] if tahap2_row is not None else 0
            row[branch] = value
            rlm_total += value
        row[rlm_columns[rlm]] = rlm_total

    row["TOTAL"] = sum(row[rlm_columns[rlm]] for rlm in ordered_rlms)
    rows.append(row)

    # ======================================================
    # TAHAP 1
    # ======================================================
    row = {"": "Tahap 1"}
    for rlm in ordered_rlms:
        rlm_total = 0
        for branch in rlm_by_cab[rlm]:
            value = tahap1_row[branch] if tahap1_row is not None else 0
            row[branch] = value
            rlm_total += value
        row[rlm_columns[rlm]] = rlm_total

    row["TOTAL"] = sum(row[rlm_columns[rlm]] for rlm in ordered_rlms)
    rows.append(row)

    # ======================================================
    # TOTAL PROPOSAL
    # ======================================================
    row = {"": "TOTAL PROPOSAL"}
    for rlm in ordered_rlms:
        rlm_total = 0
        for branch in rlm_by_cab[rlm]:
            tahap1 = tahap1_row[branch] if tahap1_row is not None else 0
            tahap2 = tahap2_row[branch] if tahap2_row is not None else 0
            value = tahap1 + tahap2
            row[branch] = value
            rlm_total += value
        row[rlm_columns[rlm]] = rlm_total

    row["TOTAL"] = sum(row[rlm_columns[rlm]] for rlm in ordered_rlms)
    rows.append(row)

    # ======================================================
    # VARIANCE
    # ======================================================
    row = {"": "Variance"}
    target_row = rows[0]
    proposal_row = rows[3]

    for column in display_columns:
        row[column] = proposal_row[column] - target_row[column]

    row["TOTAL"] = sum(row[rlm_columns[rlm]] for rlm in ordered_rlms)
    rows.append(row)

    return pd.DataFrame(rows)


# ==========================================================
# TABLE 3 - DETAIL PROGRESS
# ==========================================================

def build_detail_table(matrix, branches):

    ordered_rlms = matrix.attrs.get("ordered_rlms", [])
    rlm_by_cab = matrix.attrs.get("rlm_by_cab", {})
    rlm_columns = matrix.attrs.get("rlm_columns", {})
    display_columns = matrix.attrs.get("display_columns", branches)

    rows = []

    def add_source_row(source, label):
        row = {"": label}

        for rlm in ordered_rlms:
            rlm_total = 0
            for branch in rlm_by_cab[rlm]:
                value = source[branch]
                row[branch] = value
                rlm_total += value
            row[rlm_columns[rlm]] = rlm_total

        row["TOTAL"] = sum(row[rlm_columns[rlm]] for rlm in ordered_rlms)
        rows.append(row)

    # ======================================================
    # TAHAP 2
    # ======================================================
    for progress in TAHAP2_ORDER:
        source = matrix[matrix["PROGRESS"] == progress]
        if source.empty:
            continue
        add_source_row(source.iloc[0], progress)

    # ------------------------------------------------------
    # TOTAL TAHAP 2
    # ------------------------------------------------------
    source = matrix[matrix["PROGRESS"] == "TOTAL TAHAP 2"]
    if not source.empty:
        add_source_row(source.iloc[0], "TOTAL TAHAP 2")

    # ======================================================
    # TAHAP 1
    # ======================================================
    for progress in TAHAP1_ORDER:
        source = matrix[matrix["PROGRESS"] == progress]
        if source.empty:
            continue
        add_source_row(source.iloc[0], progress)

    # ------------------------------------------------------
    # TOTAL TAHAP 1
    # ------------------------------------------------------
    source = matrix[matrix["PROGRESS"] == "TOTAL TAHAP 1"]
    if not source.empty:
        add_source_row(source.iloc[0], "TOTAL TAHAP 1")

    detail = pd.DataFrame(rows)
    detail.attrs["branches"] = branches
    detail.attrs["ordered_rlms"] = ordered_rlms
    detail.attrs["rlm_by_cab"] = rlm_by_cab
    detail.attrs["rlm_columns"] = rlm_columns
    detail.attrs["display_columns"] = display_columns
    return detail


# ==========================================================
# RENDER
# ==========================================================

def style_aligned_table(styler, df, first_col_percent=20):
    """
    Samakan posisi kolom Tabel 2 dan Tabel 3:
    - lebar tabel 100%
    - kolom pertama memiliki lebar yang sama
    - seluruh kolom cabang + TOTAL dibagi rata
    """
    column_count = len(df.columns)

    if column_count <= 1:
        return styler

    remaining_percent = 100 - first_col_percent
    other_percent = remaining_percent / (column_count - 1)

    table_styles = [
        {
            "selector": "table",
            "props": [
                ("width", "100% !important"),
                ("table-layout", "fixed !important"),
            ],
        },
        {
            "selector": "th.col0, td.col0",
            "props": [
                ("width", f"{first_col_percent}% !important"),
            ],
        },
    ]

    for col_idx in range(1, column_count):
        table_styles.append({
            "selector": f"th.col{col_idx}, td.col{col_idx}",
            "props": [
                ("width", f"{other_percent}% !important"),
            ],
        })

    return styler.set_table_styles(
        table_styles,
        overwrite=False
    )


def style_rlm_headers(styler, df, rlm_columns):
    """
    Header kolom subtotal RLM diberi warna ungu agar berbeda dari CAB.
    Nama yang ditampilkan tetap nama RLM saja.
    """
    purple = "#D9B3FF"

    for column_index, column_name in enumerate(df.columns):
        if column_name in rlm_columns.values():
            styler = styler.set_table_styles([
                {
                    "selector": f"thead th.col{column_index}",
                    "props": [
                        ("background-color", f"{purple} !important"),
                        ("color", "#000000 !important"),
                        ("font-weight", "700 !important"),
                        ("text-align", "center !important"),
                    ],
                },
            ], overwrite=False)

    return styler


def style_detail_dataframe(df, target_go_by_branch=None):
    """
    Styling Tabel 3:
    - Header biru, tulisan hitam.
    - TOTAL TAHAP 2 dan TOTAL TAHAP 1 bold.
    - Garis hitam tebal sebagai pemisah.
    - Angka negatif merah.
    - Cell progress per cabang diberi hijau berdasarkan cumulative
      sampai mencapai Target GO dari Tabel 2.
    - Jika target terlewati pada suatu progress, seluruh cell progress
      tersebut tetap hijau; tidak ada partial coloring.
    """
    styler = df.style.format(
        lambda value: format_number(value)
        if isinstance(value, (int, float))
        else value
    )

    styler = styler.set_properties(
        **{
            "font-weight": "700",
        }
    )

    # Border seluruh tabel Tabel 3: hitam 1px.
    styler = styler.set_table_styles([
        {
            "selector": "table",
            "props": [
                ("border-collapse", "collapse !important"),
                ("border", "1px solid #000000 !important"),
            ],
        },
        {
            "selector": "thead th",
            "props": [
                ("border", "1px solid #000000 !important"),
            ],
        },
    ], overwrite=False)

    # Paksa border pada setiap cell body dan header.
    styler = styler.set_properties(
        **{
            "border": "1px solid #000000 !important",
        }
    )

    # Header biru
    styler = styler.set_table_styles([
        {
            "selector": "thead th",
            "props": [
                ("background-color", "#9DC3E6 !important"),
                ("color", "#000000 !important"),
                ("font-weight", "700 !important"),
                ("text-align", "center !important"),
            ],
        },
        {
            "selector": "th.col_heading",
            "props": [
                ("background-color", "#9DC3E6 !important"),
                ("color", "#000000 !important"),
                ("font-weight", "700 !important"),
            ],
        },
        {
            "selector": "th.blank",
            "props": [
                ("background-color", "#9DC3E6 !important"),
            ],
        },
    ])

    # Pastikan border header Tabel 3 juga tampil
    styler = styler.set_table_styles([
        {
            "selector": "thead th",
            "props": [
                ("border", "1px solid #000000 !important"),
            ],
        },
        {
            "selector": "thead th.col_heading",
            "props": [
                ("border", "1px solid #000000 !important"),
            ],
        },
        {
            "selector": "thead th.blank",
            "props": [
                ("border", "1px solid #000000 !important"),
            ],
        },
    ], overwrite=False)

    # Header subtotal RLM diberi warna ungu.
    rlm_columns = df.attrs.get("rlm_columns", {})
    styler = style_rlm_headers(
        styler,
        df,
        rlm_columns=rlm_columns,
    )

    # Angka negatif merah
    def color_negative(value):
        try:
            if pd.notna(value) and float(value) < 0:
                return "color: red; font-weight: 700;"
        except (ValueError, TypeError):
            pass
        return ""

    numeric_columns = df.select_dtypes(include=["number"]).columns
    if len(numeric_columns) > 0:
        styler = styler.map(color_negative, subset=numeric_columns)

    # Cumulative Target GO
    target_go_by_branch = target_go_by_branch or {}

    if "" in df.columns:
        branches = [
            col for col in df.attrs.get("branches", [])
            if col in df.columns
        ]
        ordered_rlms = df.attrs.get("ordered_rlms", [])
        rlm_by_cab = df.attrs.get("rlm_by_cab", {})
        rlm_columns = df.attrs.get("rlm_columns", {})

        cumulative = {branch: 0 for branch in branches}
        target_reached = {branch: False for branch in branches}

        # Target dan cumulative per RLM adalah penjumlahan seluruh CAB
        # yang berada di bawah RLM tersebut.
        target_go_by_rlm = {}
        cumulative_rlm = {}
        rlm_target_reached = {}

        for rlm in ordered_rlms:
            target = sum(
                target_go_by_branch.get(normalize(branch), 0)
                for branch in rlm_by_cab.get(rlm, [])
            )
            target_go_by_rlm[rlm] = target
            cumulative_rlm[rlm] = 0
            rlm_target_reached[rlm] = False

        # TOTAL menggunakan target kumulatif dari seluruh RLM/CAB.
        total_target = sum(target_go_by_rlm.values())
        cumulative_total = 0
        total_target_reached = False

        for idx in df.index:
            progress = str(df.at[idx, ""])

            # Baris total tahap tidak menambah cumulative karena nilainya
            # sudah merupakan agregasi dari progress-progress sebelumnya.
            if progress in ["TOTAL TAHAP 2", "TOTAL TAHAP 1"]:
                if total_target > 0 and cumulative_total >= total_target:
                    styler = styler.set_properties(
                        subset=pd.IndexSlice[idx, "TOTAL"],
                        **{"background-color": "#C6E0B4"}
                    )

                for rlm in ordered_rlms:
                    rlm_col = rlm_columns.get(rlm)
                    target = target_go_by_rlm.get(rlm, 0)
                    if (
                        rlm_col in df.columns
                        and target > 0
                        and cumulative_rlm[rlm] >= target
                    ):
                        styler = styler.set_properties(
                            subset=pd.IndexSlice[idx, rlm_col],
                            **{"background-color": "#C6E0B4"}
                        )

                for branch in branches:
                    target = target_go_by_branch.get(
                        normalize(branch), 0
                    )
                    if target > 0 and cumulative[branch] >= target:
                        styler = styler.set_properties(
                            subset=pd.IndexSlice[idx, branch],
                            **{"background-color": "#C6E0B4"}
                        )
                continue

            # --------------------------------------------------
            # Logic per CABANG
            # --------------------------------------------------
            for branch in branches:
                if target_reached[branch]:
                    continue

                try:
                    value = float(df.at[idx, branch])
                except (ValueError, TypeError):
                    value = 0

                target = target_go_by_branch.get(
                    normalize(branch), 0
                )

                if target <= 0:
                    continue

                cumulative[branch] += value

                styler = styler.set_properties(
                    subset=pd.IndexSlice[idx, branch],
                    **{"background-color": "#C6E0B4"}
                )

                if cumulative[branch] >= target:
                    target_reached[branch] = True

            # --------------------------------------------------
            # Logic per RLM - sama seperti CABANG
            # --------------------------------------------------
            for rlm in ordered_rlms:
                if rlm_target_reached[rlm]:
                    continue

                rlm_col = rlm_columns.get(rlm)
                if rlm_col not in df.columns:
                    continue

                try:
                    value = float(df.at[idx, rlm_col])
                except (ValueError, TypeError):
                    value = 0

                target = target_go_by_rlm.get(rlm, 0)
                if target <= 0:
                    continue

                cumulative_rlm[rlm] += value

                styler = styler.set_properties(
                    subset=pd.IndexSlice[idx, rlm_col],
                    **{"background-color": "#C6E0B4"}
                )

                if cumulative_rlm[rlm] >= target:
                    rlm_target_reached[rlm] = True

            # --------------------------------------------------
            # Logic kolom TOTAL - sama seperti CABANG dan RLM
            # --------------------------------------------------
            if not total_target_reached and total_target > 0:
                try:
                    total_value = float(df.at[idx, "TOTAL"])
                except (ValueError, TypeError):
                    total_value = 0

                cumulative_total += total_value

                styler = styler.set_properties(
                    subset=pd.IndexSlice[idx, "TOTAL"],
                    **{"background-color": "#C6E0B4"}
                )

                if cumulative_total >= total_target:
                    total_target_reached = True

    # Total Tahap 2 -> biru muda + bold
    if "" in df.columns:
        rows = df.index[df[""] == "TOTAL TAHAP 2"].tolist()
        if rows:
            styler = styler.set_properties(
                subset=pd.IndexSlice[rows[0], :],
                **{
                    "background-color": "#D9EAF7",
                    "font-weight": "700",
                }
            )

        # Total Tahap 1 -> kuning muda + bold
        rows = df.index[df[""] == "TOTAL TAHAP 1"].tolist()
        if rows:
            styler = styler.set_properties(
                subset=pd.IndexSlice[rows[0], :],
                **{
                    "background-color": "#FFF2CC",
                    "font-weight": "700",
                }
            )

    return styler


def show_progress_matrix(df):
    # Mobile responsive:
    # seluruh tabel tetap masuk viewport tanpa horizontal scroll,
    # tetapi dibuat sedikit lebih besar dan row diberi napas vertikal.
    # Desktop tidak berubah.

    st.markdown(
        """
        <style>
        .responsive-matrix {
            width: 100% !important;
            max-width: 100% !important;
            overflow: hidden !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        .responsive-matrix table {
            width: 100% !important;
            max-width: 100% !important;
            table-layout: fixed !important;
            border-collapse: collapse !important;
        }

        @media screen and (max-width: 768px) {
            .matrix-title {
                margin-top: -55px !important;
                margin-bottom: 18px !important;
                line-height: 1.1 !important;
            }

            .responsive-matrix table {
                min-width: 0 !important;
                font-size: 9px !important;
            }

            .responsive-matrix table th,
            .responsive-matrix table td {
                min-width: 0 !important;
                max-width: none !important;
                box-sizing: border-box !important;
                padding: 3px 1px !important;
                white-space: normal !important;
                overflow: hidden !important;
                overflow-wrap: anywhere !important;
                word-break: break-word !important;
                line-height: 1.18 !important;
                text-align: center !important;
            }

            .responsive-matrix table th.col0,
            .responsive-matrix table td.col0 {
                width: 23% !important;
            }

            .responsive-matrix table th:not(.col0),
            .responsive-matrix table td:not(.col0) {
                width: auto !important;
            }

            /* Tabel KPI lebih lega karena kolomnya lebih sedikit. */
            .responsive-kpi table {
                font-size: 10px !important;
            }

            .responsive-kpi table th,
            .responsive-kpi table td {
                padding: 6px 3px !important;
                line-height: 1.2 !important;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Paksa warna header dataframe Streamlit.
    # Selector dibuat cukup spesifik agar tidak bergantung pada hasil Styler saja.
    st.markdown(
        """
        <style>
        div[data-testid="stDataFrame"] thead th,
        div[data-testid="stDataFrame"] th.col_heading,
        div[data-testid="stDataFrame"] th.blank {
            background-color: #D9EAF7 !important;
            color: #000000 !important;
            font-weight: 700 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    matrix = build_progress_matrix(df)

    if matrix.empty:
        st.info(
            "Tidak ada data untuk ditampilkan."
        )
        return

    # Hanya CAB yang dipakai untuk mengambil Budget & GO.
    # Kolom subtotal RLM tetap ditampilkan, tetapi bukan CAB baru.
    branches = matrix.attrs.get("branches", [])

    # ======================================================
    # BUDGET & GO PER CABANG (UNTUK TABEL 2 DAN TABEL 3)
    # ======================================================

    budget_go = calculate_branch_budget_go(
        tuple(branches)
    )

    # ======================================================
    # TOTAL BUDGET & GO (UNTUK TABEL 1)
    # Mengikuti metode Budget KPI: kolom TOTAL per LOCAM.
    # ======================================================

    total_budget, total_go = calculate_overall_budget_go()

    # ======================================================
    # TOTAL TAHAP 1 & TAHAP 2
    # ======================================================

    tahap1_row = matrix[
        matrix["PROGRESS"] == "TOTAL TAHAP 1"
    ]

    tahap2_row = matrix[
        matrix["PROGRESS"] == "TOTAL TAHAP 2"
    ]

    total_tahap1 = (
        int(tahap1_row["TOTAL"].iloc[0])
        if not tahap1_row.empty
        else 0
    )

    total_tahap2 = (
        int(tahap2_row["TOTAL"].iloc[0])
        if not tahap2_row.empty
        else 0
    )

    # ======================================================
    # TITLE
    # ======================================================

    st.markdown(
        '<h3 class="matrix-title">Kekurangan GO s.d Des 2026</h3>',
        unsafe_allow_html=True,
    )

    # ======================================================
    # TABLE 1
    # ======================================================

    show_kpi_summary(
        total_budget=total_budget,
        total_go=total_go,
        total_tahap1=total_tahap1,
        total_tahap2=total_tahap2,
    )

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ======================================================
    # TABLE 2
    # ======================================================

    branch_summary = build_branch_summary(
        branches=branches,
        budget_go=budget_go,
        matrix=matrix,
    )

    branch_styler = style_branch_summary(
        branch_summary,
        rlm_columns=matrix.attrs.get("rlm_columns", {}),
    )

    # Samakan posisi kolom Tabel 2 dengan Tabel 3.
    branch_styler = style_aligned_table(
        branch_styler,
        branch_summary,
        first_col_percent=20,
    )

    # Gunakan HTML agar styling Pandas Styler tetap diterapkan.
    st.markdown(
        '<div class="responsive-matrix">'
        + branch_styler.hide(axis="index").to_html()
        + '</div>',
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ======================================================
    # TABLE 3
    # ======================================================

    detail_table = build_detail_table(
        matrix=matrix,
        branches=branches,
    )

    # Target GO Tabel 2 menjadi acuan cumulative Tabel 3.
    target_go_by_branch = {}

    target_rows = branch_summary[
        branch_summary[""] == "Target GO"
    ]

    if not target_rows.empty:
        target_row = target_rows.iloc[0]

        for branch in branches:
            try:
                target_go_by_branch[normalize(branch)] = float(
                    target_row[branch]
                )
            except (ValueError, TypeError):
                target_go_by_branch[normalize(branch)] = 0

    detail_styler = style_detail_dataframe(
        detail_table,
        target_go_by_branch=target_go_by_branch,
    )

    # Gunakan proporsi kolom yang sama dengan Tabel 2.
    detail_styler = style_aligned_table(
        detail_styler,
        detail_table,
        first_col_percent=20,
    )

    st.markdown(
        '<div class="responsive-matrix">'
        + detail_styler.hide(axis="index").to_html()
        + '</div>',
        unsafe_allow_html=True,
    )
