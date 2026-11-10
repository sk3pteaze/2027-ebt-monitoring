import streamlit as st
import gspread
import pandas as pd

from google.oauth2.service_account import Credentials
from config import SPREADSHEET_ID

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]


def load_users():

    credentials = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPES
    )

    client = gspread.authorize(credentials)

    spreadsheet = client.open_by_key(SPREADSHEET_ID)

    worksheet = spreadsheet.worksheet("USERS")

    data = worksheet.get_all_records()

    return pd.DataFrame(data)

def authenticate(username, password):

    users = load_users()

    user = users[
        (users["USERNAME"].astype(str).str.strip() == username.strip())
        &
        (users["PASSWORD"].astype(str).str.strip() == password.strip())
        &
        (users["AKTIF"].astype(str).str.upper() == "TRUE")
    ]

    if user.empty:
        return None

    return user.iloc[0]