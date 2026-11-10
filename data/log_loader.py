import streamlit as st
import gspread
import pandas as pd

from google.oauth2.service_account import Credentials

from config import SPREADSHEET_ID, LOG_SHEET


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]


@st.cache_data(ttl=300)
def load_log():

    credentials = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPES
    )

    client = gspread.authorize(credentials)

    spreadsheet = client.open_by_key(
        SPREADSHEET_ID
    )

    worksheet = spreadsheet.worksheet(
        LOG_SHEET
    )

    data = worksheet.get_all_values()

    if not data:
        return pd.DataFrame()

    headers = data[0]
    rows = data[1:]

    # Bersihkan header kosong
    valid_columns = [
        i
        for i, header in enumerate(headers)
        if str(header).strip() != ""
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

    df = pd.DataFrame(
        rows,
        columns=headers
    )

    return df