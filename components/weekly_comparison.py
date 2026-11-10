import streamlit as st
import pandas as pd

from data.log_loader import load_log


# ==========================================================
# HELPER
# ==========================================================

def clean_value(value):
    if value is None:
        return ""

    try:
        if pd.isna(value):
            return ""
    except Exception:
        pass

    return str(value).strip()


def normalize_text(value):
    return " ".join(
        clean_value(value).upper().split()
    )


def values_equal(value1, value2):

    value1 = clean_value(value1)
    value2 = clean_value(value2)

    date1 = pd.to_datetime(
        value1,
        errors="coerce"
    )

    date2 = pd.to_datetime(
        value2,
        errors="coerce"
    )

    if pd.notna(date1) and pd.notna(date2):

        return date1.date() == date2.date()

    return normalize_text(value1) == normalize_text(value2)


# ==========================================================
# LOAD LOG
# ==========================================================

@st.cache_data(ttl=300)
def prepare_log():

    log_df = load_log()

    if log_df is None or log_df.empty:
        return pd.DataFrame()

    required_columns = [
        "Snapshot Date",
        "Proposal",
        "Field",
        "Old Value",
        "New Value"
    ]

    missing_columns = [
        col
        for col in required_columns
        if col not in log_df.columns
    ]

    if missing_columns:

        st.error(
            "Kolom LOG tidak ditemukan: "
            + ", ".join(missing_columns)
        )

        return pd.DataFrame()

    df = log_df.copy()

    # ------------------------------------------------------
    # SNAPSHOT DATE
    # ------------------------------------------------------

    df["_snapshot_date"] = pd.to_datetime(
        df["Snapshot Date"],
        errors="coerce"
    )

    df = df[
        df["_snapshot_date"].notna()
    ].copy()

    # ------------------------------------------------------
    # PROPOSAL
    # ------------------------------------------------------

    df["_proposal"] = (
        df["Proposal"]
        .apply(normalize_text)
    )

    # ------------------------------------------------------
    # FIELD
    # ------------------------------------------------------

    df["_field"] = (
        df["Field"]
        .apply(normalize_text)
    )

    # ------------------------------------------------------
    # TIMESTAMP
    # ------------------------------------------------------

    if "Timestamp" in df.columns:

        df["_timestamp"] = pd.to_datetime(
            df["Timestamp"],
            errors="coerce"
        )

    else:

        df["_timestamp"] = pd.NaT

    return df


# ==========================================================
# AVAILABLE SNAPSHOT DATES
# ==========================================================

def get_available_dates():

    log_df = prepare_log()

    if log_df.empty:
        return []

    return sorted(
        log_df["_snapshot_date"]
        .dt.date
        .dropna()
        .unique()
    )


# ==========================================================
# DATE PICKER
# ==========================================================

def show_comparison_picker(reset_token=0):

    available_dates = get_available_dates()

    if not available_dates:

        st.info(
            "Belum ada Snapshot Date di LOG."
        )

        return None

    # ------------------------------------------------------
    # DEFAULT
    # ------------------------------------------------------

    if len(available_dates) >= 2:

        default_range = (
            available_dates[-2],
            available_dates[-1]
        )

    else:

        default_range = (
            available_dates[0],
            available_dates[0]
        )

    st.markdown(
        "### 📅 Perbandingan Snapshot"
    )

    # ------------------------------------------------------
    # KEY DINAMIS
    #
    # Ketika proposal di-clear, reset_token berubah.
    # Akibatnya date_input dianggap widget baru dan
    # otomatis kembali ke default_range.
    # ------------------------------------------------------

    date_picker_key = (
        f"snapshot_comparison_range_{reset_token}"
    )

    selected_range = st.date_input(
        "Pilih 2 tanggal untuk dibandingkan",
        value=default_range,
        min_value=available_dates[0],
        max_value=available_dates[-1],
        key=date_picker_key,
        format="DD/MM/YYYY"
    )

    # ------------------------------------------------------
    # VALIDASI
    # ------------------------------------------------------

    if not isinstance(
        selected_range,
        (tuple, list)
    ):

        st.warning(
            "Pilih 2 tanggal snapshot."
        )

        return None

    if len(selected_range) != 2:

        st.warning(
            "Pilih tepat 2 tanggal snapshot."
        )

        return None

    old_date = selected_range[0]
    new_date = selected_range[1]

    # ------------------------------------------------------
    # URUTAN
    # ------------------------------------------------------

    if old_date >= new_date:

        st.warning(
            "Snapshot pertama harus lebih awal "
            "dari snapshot kedua."
        )

        return None

    # ------------------------------------------------------
    # HARUS EXACT SNAPSHOT
    # ------------------------------------------------------

    available_set = set(
        available_dates
    )

    if old_date not in available_set:

        st.warning(
            f"Tidak ada snapshot pada "
            f"{old_date.strftime('%d-%m-%Y')}."
        )

        return None

    if new_date not in available_set:

        st.warning(
            f"Tidak ada snapshot pada "
            f"{new_date.strftime('%d-%m-%Y')}."
        )

        return None

    # ------------------------------------------------------
    # SESSION STATE
    # ------------------------------------------------------

    st.session_state[
        "snapshot_old_date"
    ] = old_date

    st.session_state[
        "snapshot_new_date"
    ] = new_date

    return old_date, new_date
    # ------------------------------------------------------
    # SESSION STATE
    # ------------------------------------------------------

    st.session_state[
        "snapshot_old_date"
    ] = old_date

    st.session_state[
        "snapshot_new_date"
    ] = new_date

    return old_date, new_date


# ==========================================================
# GET SELECTED DATE
# ==========================================================

def get_comparison_dates():

    return (
        st.session_state.get(
            "snapshot_old_date"
        ),
        st.session_state.get(
            "snapshot_new_date"
        )
    )


# ==========================================================
# GET EXACT SNAPSHOT
# ==========================================================

def get_exact_snapshot(
    proposal_log,
    snapshot_date
):

    snapshot = proposal_log[
        proposal_log["_snapshot_date"].dt.date
        ==
        snapshot_date
    ].copy()

    if snapshot.empty:
        return pd.DataFrame()

    # ------------------------------------------------------
    # Jika satu field berubah beberapa kali dalam
    # snapshot yang sama, ambil perubahan terakhir.
    # ------------------------------------------------------

    if "_timestamp" in snapshot.columns:

        snapshot = snapshot.sort_values(
            "_timestamp",
            ascending=True,
            na_position="first"
        )

    snapshot = (
        snapshot
        .drop_duplicates(
            subset=["_field"],
            keep="last"
        )
    )

    return snapshot


# ==========================================================
# GET VALUE FROM EXACT SNAPSHOT
# ==========================================================

def get_snapshot_value(
    snapshot_df,
    field
):

    if snapshot_df.empty:
        return None

    field_normalized = normalize_text(
        field
    )

    result = snapshot_df[
        snapshot_df["_field"]
        ==
        field_normalized
    ]

    if result.empty:
        return None

    row = result.iloc[-1]

    return clean_value(
        row["New Value"]
    )


# ==========================================================
# COMPARE EXACT TWO SNAPSHOTS
# ==========================================================

def compare_snapshots(
    selected_proposal
):

    log_df = prepare_log()

    if log_df.empty:
        return pd.DataFrame()

    old_date, new_date = (
        get_comparison_dates()
    )

    if old_date is None or new_date is None:
        return pd.DataFrame()

    proposal_normalized = normalize_text(
        selected_proposal
    )

    proposal_log = log_df[
        log_df["_proposal"]
        ==
        proposal_normalized
    ].copy()

    if proposal_log.empty:
        return pd.DataFrame()

    # ======================================================
    # PENTING:
    #
    # HANYA SNAPSHOT YANG DIPILIH
    #
    # 11 -> 16
    #
    # snapshot 15 TIDAK MASUK DI SINI
    # ======================================================

    old_snapshot = get_exact_snapshot(
        proposal_log,
        old_date
    )

    new_snapshot = get_exact_snapshot(
        proposal_log,
        new_date
    )

    # ------------------------------------------------------
    # Salah satu snapshot tidak memiliki LOG
    # ------------------------------------------------------

    if old_snapshot.empty:
        return pd.DataFrame()

    if new_snapshot.empty:
        return pd.DataFrame()

    # ======================================================
    # FIELD YANG ADA DI KEDUA SNAPSHOT
    # ======================================================

    old_fields = set(
        old_snapshot["_field"]
    )

    new_fields = set(
        new_snapshot["_field"]
    )

    common_fields = sorted(
        old_fields
        &
        new_fields
    )

    changes = []

    for field in common_fields:

        old_value = get_snapshot_value(
            old_snapshot,
            field
        )

        new_value = get_snapshot_value(
            new_snapshot,
            field
        )

        # --------------------------------------------------
        # HANYA FIELD YANG BENAR-BENAR BERUBAH
        # --------------------------------------------------

        if values_equal(
            old_value,
            new_value
        ):

            continue

        # Ambil nama field asli
        old_row = old_snapshot[
            old_snapshot["_field"]
            ==
            field
        ].iloc[-1]

        changes.append({

            "Field": old_row["Field"],

            "Old Value": old_value,

            "New Value": new_value,

        })

    return pd.DataFrame(
        changes
    )


# ==========================================================
# DAY DIFFERENCE
# ==========================================================

def calculate_day_diff(
    old_value,
    new_value
):

    old_date = pd.to_datetime(
        old_value,
        errors="coerce"
    )

    new_date = pd.to_datetime(
        new_value,
        errors="coerce"
    )

    if (
        pd.isna(old_date)
        or
        pd.isna(new_date)
    ):

        return None

    return (
        new_date.date()
        -
        old_date.date()
    ).days


# ==========================================================
# WEEKLY COMPARISON DISPLAY
# ==========================================================

def show_weekly_comparison(
    selected_proposal
):

    st.markdown(
        "### 🔄 Perubahan Mingguan"
    )

    old_date, new_date = (
        get_comparison_dates()
    )

    if old_date is None or new_date is None:

        st.info(
            "Silakan pilih 2 Snapshot Date."
        )

        return

    # ======================================================
    # COMPARE
    # ======================================================

    comparison_df = compare_snapshots(
        selected_proposal
    )

    # ======================================================
    # PERIODE
    # ======================================================

    st.caption(
        f"Perbandingan: "
        f"{old_date.strftime('%d-%b-%Y')}"
        f" → "
        f"{new_date.strftime('%d-%b-%Y')}"
    )

    # ======================================================
    # NO CHANGE
    # ======================================================

    if comparison_df.empty:

        st.success(
            "Tidak ada perubahan antara "
            "kedua snapshot."
        )

        return

    # ======================================================
    # SUMMARY
    # ======================================================

    total_changes = len(
        comparison_df
    )

    field_upper = (
        comparison_df["Field"]
        .astype(str)
        .str.upper()
    )

    progress_changes = comparison_df[
        field_upper.str.contains(
            "PROGRESS|TAHAPAN",
            regex=True,
            na=False
        )
    ]

    date_changes = comparison_df[
        field_upper.str.contains(
            "TGL|DATE",
            regex=True,
            na=False
        )
    ]

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Total Perubahan",
            total_changes
        )

    with col2:

        st.metric(
            "Progress",
            len(progress_changes)
        )

    with col3:

        st.metric(
            "Tanggal",
            len(date_changes)
        )

    st.divider()

    # ======================================================
    # CHANGE CARDS
    # ======================================================

    for _, change in comparison_df.iterrows():

        field = clean_value(
            change["Field"]
        )

        old_value = clean_value(
            change["Old Value"]
        )

        new_value = clean_value(
            change["New Value"]
        )

        field_upper = field.upper()

        if (
            "PROGRESS" in field_upper
            or
            "TAHAPAN" in field_upper
        ):

            icon = "🔵"

        elif (
            "TGL" in field_upper
            or
            "DATE" in field_upper
        ):

            icon = "🟡"

        elif "STATUS" in field_upper:

            icon = "🟢"

        else:

            icon = "⚪"

        day_diff = calculate_day_diff(
            old_value,
            new_value
        )

        with st.container(
            border=True
        ):

            st.caption(
                icon
            )

            st.markdown(
                f"**{field}**"
            )

            col_old, col_arrow, col_new = (
                st.columns([4, 1, 4])
            )

            with col_old:

                st.caption(
                    "Snapshot Lama"
                )

                st.write(
                    old_value
                    if old_value
                    else "-"
                )

            with col_arrow:

                st.markdown(
                    "### →"
                )

            with col_new:

                st.caption(
                    "Snapshot Baru"
                )

                st.write(
                    new_value
                    if new_value
                    else "-"
                )

            if day_diff is not None:

                if day_diff > 0:

                    st.caption(
                        f"⏱ +{day_diff} hari"
                    )

                elif day_diff < 0:

                    st.caption(
                        f"⏱ {day_diff} hari"
                    )

                else:

                    st.caption(
                        "⏱ 0 hari"
                    )