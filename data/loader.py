
import streamlit as st
import gspread
import pandas as pd

from google.oauth2.service_account import Credentials

from config import (
    SPREADSHEET_ID,
    MASTER_SHEET,
    MAPPING_WORKSHEET_NAME,
    PROGRESS_SM,
    PROGRESS_LOCAM_NEW
)


# ==========================================================
# GOOGLE SHEETS CONFIGURATION
# ==========================================================

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]


# ==========================================================
# NORMALISASI HEADER
# ==========================================================

def normalize_headers(df):

    df.columns = (
        df.columns
        .astype(str)
        .str.replace("\n", " ", regex=False)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
        .str.upper()
    )

    return df


# ==========================================================
# NORMALISASI VALUE
# ==========================================================

def normalize_value(series):

    return (
        series
        .astype(str)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
        .str.upper()
    )


# ==========================================================
# CONNECT GOOGLE SHEETS
# ==========================================================

def connect_google_sheets():

    credentials = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPES
    )

    client = gspread.authorize(credentials)

    spreadsheet = client.open_by_key(
        SPREADSHEET_ID
    )

    return spreadsheet


# ==========================================================
# LOAD DATA MASTER
# ==========================================================

@st.cache_data(ttl=300)
def load_data():

    spreadsheet = connect_google_sheets()

    # ======================================================
    # LOAD MASTER_COPY
    # ======================================================

    master_sheet = spreadsheet.worksheet(
        MASTER_SHEET
    )

    master_data = master_sheet.get_all_values()

    if not master_data:
        return pd.DataFrame()

    headers = [
        str(col).strip()
        for col in master_data[0]
    ]

    rows = master_data[1:]

    # ======================================================
    # BUANG KOLOM HEADER KOSONG
    # ======================================================

    valid_columns = [
        i
        for i, header in enumerate(headers)
        if header.strip() != ""
    ]

    headers = [
        headers[i]
        for i in valid_columns
    ]

    rows = [
        [
            row[i] if i < len(row) else ""
            for i in valid_columns
        ]
        for row in rows
    ]

    # ======================================================
    # DATAFRAME MASTER
    # ======================================================

    df = pd.DataFrame(
        rows,
        columns=headers
    )

    # ======================================================
    # NORMALISASI HEADER
    # ======================================================

    df = normalize_headers(df)

    # ======================================================
    # FILTER R/F = R
    # ======================================================

    if "R/F" not in df.columns:

        raise ValueError(
            "Kolom R/F tidak ditemukan.\n"
            f"Kolom tersedia: {df.columns.tolist()}"
        )

    df["R/F"] = normalize_value(
        df["R/F"]
    )

    df = df[
        df["R/F"] == "R"
    ].copy()

    # ======================================================
    # LOAD TAHAPAN_MAPPING
    # ======================================================

    mapping_sheet = spreadsheet.worksheet(
        MAPPING_WORKSHEET_NAME
    )

    mapping_data = mapping_sheet.get_all_values()

    if not mapping_data:

        df["TAHAPAN"] = None

        return df

    # ======================================================
    # AMBIL DATA MAPPING
    # ======================================================

    mapping_headers = [
        str(col).strip()
        for col in mapping_data[0]
    ]

    mapping_rows = mapping_data[1:]

    if len(mapping_headers) < 2:

        raise ValueError(
            "TAHAPAN_MAPPING harus memiliki minimal "
            "2 kolom: MASTER_PROGRESS_MAPPING dan TAHAPAN_MAPPING."
        )

    # ======================================================
    # DATAFRAME MAPPING
    # ======================================================

    mapping_df = pd.DataFrame(
        mapping_rows
    )

    if mapping_df.shape[1] < 2:

        raise ValueError(
            "Worksheet TAHAPAN_MAPPING "
            "tidak memiliki minimal 2 kolom."
        )

    mapping_df = mapping_df.iloc[:, :2].copy()

    mapping_df.columns = [
        "MASTER_PROGRESS_MAPPING",
        "TAHAPAN_MAPPING"
    ]

    # ======================================================
    # NORMALISASI MAPPING
    # ======================================================

    mapping_df["MASTER_PROGRESS_MAPPING"] = (
        normalize_value(
            mapping_df["MASTER_PROGRESS_MAPPING"]
        )
    )

    mapping_df["TAHAPAN_MAPPING"] = (
        normalize_value(
            mapping_df["TAHAPAN_MAPPING"]
        )
    )

    # ======================================================
    # HAPUS MAPPING KOSONG
    # ======================================================

    mapping_df = mapping_df[
        (mapping_df["MASTER_PROGRESS_MAPPING"] != "") &
        (mapping_df["MASTER_PROGRESS_MAPPING"] != "NAN") &
        (mapping_df["TAHAPAN_MAPPING"] != "") &
        (mapping_df["TAHAPAN_MAPPING"] != "NAN")
    ].copy()

    # ======================================================
    # BUILD DICTIONARY MAPPING
    # ======================================================

    mapping = dict(
        zip(
            mapping_df["MASTER_PROGRESS_MAPPING"],
            mapping_df["TAHAPAN_MAPPING"]
        )
    )

    # ======================================================
    # TAHAPAN 2
    # ↓
    # TAHAPAN
    # ======================================================

    if "TAHAPAN 2" not in df.columns:

        raise ValueError(
            "Kolom TAHAPAN 2 tidak ditemukan.\n"
            f"Kolom tersedia: {df.columns.tolist()}"
        )

    df["TAHAPAN"] = (
        normalize_value(
            df["TAHAPAN 2"]
        )
        .map(mapping)
    )

    return df


# ==========================================================
# LOAD PROGRESS SM
# ==========================================================

@st.cache_data(ttl=300)
def load_progress_sm():

    spreadsheet = connect_google_sheets()

    progress_sm_sheet = spreadsheet.worksheet(
        PROGRESS_SM
    )

    progress_sm_data = (
        progress_sm_sheet.get_all_values()
    )

    if not progress_sm_data:
        return pd.DataFrame()

    return pd.DataFrame(
        progress_sm_data
    )


# ==========================================================
# LOAD PROGRESS LOCAM NEW
# ==========================================================

@st.cache_data(ttl=300)
def load_progress_locam_new():

    spreadsheet = connect_google_sheets()

    sheet = spreadsheet.worksheet(
        PROGRESS_LOCAM_NEW
    )

    data = sheet.get_all_values()

    if not data:
        return pd.DataFrame()

    return pd.DataFrame(
        data
    )
