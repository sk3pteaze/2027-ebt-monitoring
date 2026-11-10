import html

import streamlit as st
import pandas as pd

from data.log_loader import load_log


# ==========================================================
# PROGRESSs
# ==========================================================

PROGRESS_STEPS = [

    {
        "name": "RAB",
        "status_col": "RAB",
        "estimate_col": "TGL ESTIMASI RAB",
        "real_col": "TGL REALISASI RAB",
    },

    {
        "name": "PANEL BISNIS",
        "status_col": "PANEL BISNIS",
        "estimate_col": "TGL ESTIMASI PANEL BISNIS",
        "real_col": "TGL REALISASI PANEL BISNIS",
    },

    {
        "name": "PANEL FINAL",
        "status_col": "PANEL FINAL",
        "estimate_col": "TGL ESTIMASI PANEL FINAL",
        "real_col": "TGL REALISASI PANEL FINAL",
    },

    {
        "name": "PROP HO",
        "status_col": "PROP HO",
        "estimate_col": "TGL ESTIMASI KIRIM PROP HO",
        "real_col": "TGL REALISASI KIRIM PROP HO",
    },

    {
        "name": "PROP ACC",
        "status_col": "PROP ACC",
        "estimate_col": "TGL ESTIMASI PROPOSAL ACC",
        "real_col": "TGL REALISASI PROPOSAL ACC",
    },

    {
        "name": "PROSES IJIN",
        "status_col": "PROSES IJIN",
        "estimate_col": "TGL ESTIMASI PROSES IZIN",
        "real_col": "TGL  REALISASI PROSES IZIN",
    },

    {
        "name": "NOTARIS",
        "status_col": "NOTARIS",
        "estimate_col": "TGL ESTIMASI NOTARIS",
        "real_col": "TGL REALISASI NOTARIS",
    },

    {
        "name": "RENOVASI",
        "status_col": "RENOVASI",
        "estimate_col": "TGL ESTIMASI RENOVASI",
        "real_col": "TGL REALISASI RENOVASI",
    },

    {
        "name": "SERAH TERIMA",
        "status_col": "SERAH TERIMA",
        "estimate_col": "TGL ESTIMASI SERAH TERIMA",
        "real_col": "TGL REALISASI SERAH TERIMA",
    },

    {
        "name": "GO",
        "status_col": "GO",
        "estimate_col": "TGL ESTIMASI GO",
        "real_col": "TGL REALISASI GO",
    },
]


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
        clean_value(value)
        .upper()
        .split()
    )


def format_date(value):

    value = clean_value(value)

    if not value:
        return ""

    parsed = pd.to_datetime(
        value,
        errors="coerce"
    )

    if pd.isna(parsed):
        return value

    return (
        f"{parsed.day}-"
        f"{parsed.strftime('%b')}-"
        f"{str(parsed.year)[-2:]}"
    )


def is_completed(value):

    value = normalize_text(
        value
    )

    return value in [
        "SUDAH",
        "DONE",
        "SELESAI",
        "YA",
        "YES",
        "1",
        "TRUE",
        "OK",
    ]


def values_equal(
    value1,
    value2
):

    date1 = pd.to_datetime(
        value1,
        errors="coerce"
    )

    date2 = pd.to_datetime(
        value2,
        errors="coerce"
    )

    if (
        pd.notna(date1)
        and
        pd.notna(date2)
    ):

        return (
            date1.date()
            ==
            date2.date()
        )

    return (
        normalize_text(value1)
        ==
        normalize_text(value2)
    )


# ==========================================================
# LOAD LOG
# ==========================================================

@st.cache_data(ttl=300)
def load_timeline_log():

    log_df = load_log()

    if log_df is None or log_df.empty:

        return pd.DataFrame()

    required_columns = [
        "Proposal",
        "Field",
        "Old Value",
        "New Value",
        "Snapshot Date",
    ]

    missing = [
        col
        for col in required_columns
        if col not in log_df.columns
    ]

    if missing:

        return pd.DataFrame()

    df = log_df.copy()

    df["_proposal"] = (
        df["Proposal"]
        .apply(normalize_text)
    )

    df["_field"] = (
        df["Field"]
        .apply(normalize_text)
    )

    df["_snapshot_date"] = pd.to_datetime(
        df["Snapshot Date"],
        errors="coerce"
    )

    if "Timestamp" in df.columns:

        df["_timestamp"] = pd.to_datetime(
            df["Timestamp"],
            errors="coerce"
        )

    else:

        df["_timestamp"] = pd.NaT

    return df


# ==========================================================
# GET SELECTED SNAPSHOTS
# ==========================================================

def get_snapshot_dates():

    old_date = st.session_state.get(
        "snapshot_old_date"
    )

    new_date = st.session_state.get(
        "snapshot_new_date"
    )

    return (
        old_date,
        new_date
    )


# ==========================================================
# RECONSTRUCT VALUE
# ==========================================================

def reconstruct_value(
    proposal_log,
    field,
    snapshot_date
):
    """
    Mengambil nilai field pada kondisi snapshot tertentu.

    Catatan:
    LOG bersifat change-log, jadi field tidak harus memiliki
    record tepat pada setiap tanggal. Nilai tetap direkonstruksi
    dari perubahan terakhir sebelum/pada snapshot.

    Namun, fungsi ini TIDAK menentukan apakah sebuah comparison
    valid. Validasi bahwa kedua tanggal benar-benar memiliki
    snapshot dilakukan di get_date_change_info().
    """

    field_normalized = normalize_text(
        field
    )

    field_log = proposal_log[
        proposal_log["_field"]
        ==
        field_normalized
    ].copy()

    if field_log.empty:
        return None

    field_log = field_log.sort_values(
        [
            "_snapshot_date",
            "_timestamp"
        ],
        ascending=True,
        na_position="first"
    )

    # Nilai terakhir sebelum / pada snapshot
    before = field_log[
        field_log["_snapshot_date"].dt.date
        <=
        snapshot_date
    ]

    if not before.empty:
        return clean_value(
            before.iloc[-1]["New Value"]
        )

    # Jika snapshot berada sebelum perubahan pertama,
    # gunakan Old Value dari perubahan pertama.
    after = field_log[
        field_log["_snapshot_date"].dt.date
        >
        snapshot_date
    ]

    if not after.empty:
        return clean_value(
            after.iloc[0]["Old Value"]
        )

    return None


# ==========================================================
# CHECK EXACT SNAPSHOT
# ==========================================================

def has_exact_snapshot(
    proposal_log,
    snapshot_date
):
    """
    True hanya jika proposal memiliki LOG pada tanggal
    snapshot yang dipilih.

    Ini penting agar:

        LOG: 11, 15
        pilih: 11 -> 16

    TIDAK dianggap sebagai comparison 11 -> 15.

    Sedangkan:

        LOG: 11, 15, 16
        pilih: 11 -> 16

    valid, dan hanya 11 vs 16 yang menjadi pasangan
    comparison.
    """

    if proposal_log.empty:
        return False

    return (
        proposal_log["_snapshot_date"]
        .dt.date
        .eq(snapshot_date)
        .any()
    )


# ==========================================================
# GET DATE CHANGE
# ==========================================================

def get_date_change_info(
    selected_proposal,
    field_name,
    current_value
):
    old_snapshot, new_snapshot = (
        get_snapshot_dates()
    )

    if (
        old_snapshot is None
        or
        new_snapshot is None
    ):
        return None

    log_df = load_timeline_log()

    if log_df.empty:
        return None

    proposal_normalized = normalize_text(
        selected_proposal
    )

    proposal_log = log_df[
        log_df["_proposal"]
        ==
        proposal_normalized
    ].copy()

    if proposal_log.empty:
        return None

    # ======================================================
    # EXACT SNAPSHOT VALIDATION
    # ======================================================
    #
    # Kedua tanggal HARUS benar-benar tersedia di LOG
    # untuk proposal ini.
    #
    # Jadi:
    #
    # LOG = 11, 15
    # pilih = 11 -> 16
    #
    # langsung return None.
    #
    # LOG = 11, 15, 16
    # pilih = 11 -> 16
    #
    # valid. Tanggal 15 tidak menjadi pasangan comparison.
    # ======================================================

    if not has_exact_snapshot(
        proposal_log,
        old_snapshot
    ):
        return None

    if not has_exact_snapshot(
        proposal_log,
        new_snapshot
    ):
        return None

    # ======================================================
    # RECONSTRUCT NILAI PADA EXACT SNAPSHOT
    # ======================================================

    old_value = reconstruct_value(
        proposal_log,
        field_name,
        old_snapshot
    )

    new_value = reconstruct_value(
        proposal_log,
        field_name,
        new_snapshot
    )

    if old_value is None:
        return None

    if new_value is None:
        return None

    # ======================================================
    # CURRENT DATA HARUS SESUAI SNAPSHOT BARU
    # ======================================================

    if not values_equal(
        new_value,
        current_value
    ):
        return None

    # ======================================================
    # HANYA HIGHLIGHT JIKA NILAI SNAPSHOT BERBEDA
    # ======================================================

    if values_equal(
        old_value,
        new_value
    ):
        return None

    # ======================================================
    # DAY DIFF
    # ======================================================

    old_date = pd.to_datetime(
        old_value,
        errors="coerce"
    )

    new_date = pd.to_datetime(
        new_value,
        errors="coerce"
    )

    day_diff = None

    if (
        pd.notna(old_date)
        and
        pd.notna(new_date)
    ):
        day_diff = (
            new_date.date()
            -
            old_date.date()
        ).days

    return {
        "old_value": old_value,
        "new_value": new_value,
        "day_diff": day_diff,
        "old_snapshot": old_snapshot,
        "new_snapshot": new_snapshot,
    }


# ==========================================================
# NORMAL DATE
# ==========================================================

def render_normal_date(
    label,
    value
):

    formatted = format_date(
        value
    )

    if not formatted:
        return

    st.caption(
        f"{label}: {formatted}"
    )


# ==========================================================
# CHANGED DATE
# ==========================================================

def render_changed_date(
    label,
    value,
    change_info
):

    formatted = format_date(
        value
    )

    old_value = format_date(
        change_info["old_value"]
    )

    old_snapshot = change_info[
        "old_snapshot"
    ]

    new_snapshot = change_info[
        "new_snapshot"
    ]

    day_diff = change_info[
        "day_diff"
    ]

    if day_diff is None:

        diff_text = "-"

    elif day_diff > 0:

        diff_text = (
            f"+{day_diff} hari"
        )

    elif day_diff < 0:

        diff_text = (
            f"{day_diff} hari"
        )

    else:

        diff_text = "0 hari"

    period_text = (
        f"{old_snapshot.strftime('%d-%b-%y')}"
        f" → "
        f"{new_snapshot.strftime('%d-%b-%y')}"
    )

    # ======================================================
    # ESCAPE
    # ======================================================

    safe_label = html.escape(
        str(label)
    )

    safe_current = html.escape(
        str(formatted)
    )

    safe_old = html.escape(
        str(old_value)
    )

    safe_period = html.escape(
        str(period_text)
    )

    safe_diff = html.escape(
        str(diff_text)
    )

    # ======================================================
    # HOVER
    # ======================================================

    st.html(
        f"""
        <div style="
            position:relative;
            display:inline-block;
        ">

            <div style="
                display:inline-block;
                background:#fff7ed;
                border:1px solid #fdba74;
                color:#b45309;
                border-radius:6px;
                padding:5px 8px;
                font-size:14px;
                cursor:help;
            ">

                {safe_label}:
                <strong>
                    {safe_current}
                </strong>
                🔄

            </div>

            <div
                class="timeline-tooltip"
                style="
                    visibility:hidden;
                    opacity:0;
                    position:absolute;
                    z-index:999999;
                    left:0;
                    bottom:calc(100% + 10px);
                    width:300px;
                    background:#ffffff;
                    border:1px solid #e5e7eb;
                    border-radius:10px;
                    padding:16px;
                    box-shadow:
                        0 6px 20px
                        rgba(0,0,0,0.15);
                    transition:
                        opacity 0.15s ease;
                    pointer-events:none;
                    font-family:
                        -apple-system,
                        BlinkMacSystemFont,
                        "Segoe UI",
                        sans-serif;
                "
            >

                <div style="
                    font-size:16px;
                    font-weight:600;
                    color:#27272a;
                    margin-bottom:14px;
                ">
                    📅 Perubahan Mingguan
                </div>

                <div style="
                    font-size:14px;
                    color:#71717a;
                    margin-bottom:18px;
                ">
                    Periode: {safe_period}
                </div>

                <div style="
                    display:flex;
                    justify-content:space-between;
                    margin-bottom:12px;
                    font-size:15px;
                ">

                    <span style="
                        color:#71717a;
                    ">
                        Sebelumnya
                    </span>

                    <strong>
                        {safe_old}
                    </strong>

                </div>

                <div style="
                    display:flex;
                    justify-content:space-between;
                    margin-bottom:12px;
                    font-size:15px;
                ">

                    <span style="
                        color:#71717a;
                    ">
                        Sekarang
                    </span>

                    <strong>
                        {safe_current}
                    </strong>

                </div>

                <div style="
                    display:flex;
                    justify-content:space-between;
                    font-size:15px;
                ">

                    <span style="
                        color:#71717a;
                    ">
                        Perubahan
                    </span>

                    <strong>
                        {safe_diff}
                    </strong>

                </div>

            </div>

        </div>

        <style>
            div:hover > .timeline-tooltip {{
                visibility:visible !important;
                opacity:1 !important;
            }}
        </style>
        """
    )


# ==========================================================
# TIMELINE DATE
# ==========================================================

def render_timeline_date(
    label,
    value,
    selected_proposal,
    field_name
):

    value = clean_value(
        value
    )

    if not value:
        return

    change_info = get_date_change_info(
        selected_proposal,
        field_name,
        value
    )

    if change_info is None:

        render_normal_date(
            label,
            value
        )

    else:

        render_changed_date(
            label,
            value,
            change_info
        )


# ==========================================================
# STATUS BOX
# ==========================================================

def render_status_box(
    name,
    completed
):

    if completed:

        st.markdown(
            f"""
            <div style="
                background:#e8f8ee;
                border-radius:10px;
                padding:14px;
                min-height:52px;
                display:flex;
                align-items:center;
                box-sizing:border-box;
                color:#16833b;
                font-size:16px;
                font-weight:500;
            ">
                ✓ {html.escape(str(name))}
            </div>
            """,
            unsafe_allow_html=True
        )

    else:

        st.markdown(
            f"""
            <div style="
                padding:14px 0;
                min-height:52px;
                display:flex;
                align-items:center;
                box-sizing:border-box;
                color:#3f3f46;
                font-size:16px;
            ">
                ○ {html.escape(str(name))}
            </div>
            """,
            unsafe_allow_html=True
        )


# ==========================================================
# MAIN TIMELINE
# ==========================================================

def show_progress_timeline(
    row,
    selected_proposal
):
        # Hapus nama kolom duplikat, pertahankan kolom pertama
    row = row[
        ~row.index.duplicated(keep="first")
    ]

    st.markdown(
        f"# Progress Proposal  — {selected_proposal}"
    )

    # ======================================================
    # HEADER
    # ======================================================

    tahapan = clean_value(
        row.get(
            "TAHAPAN",
            ""
        )
    )

    current_progress = clean_value(
        row.get(
            "MASTER PROGRESS",
            ""
        )
    )

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(
            f"**Tahapan:** {tahapan}"
        )

    with col2:

        st.markdown(
            f"**Current Progress:** "
            f"{current_progress}"
        )

    # ======================================================
    # COUNT
    # ======================================================

    completed_count = 0

    for step in PROGRESS_STEPS:

        if is_completed(
            row.get(
                step["status_col"],
                ""
            )
        ):

            completed_count += 1

    total_progress = len(
        PROGRESS_STEPS
    )

    progress_value = (
        completed_count
        /
        total_progress
    )

    st.progress(
        progress_value
    )

    st.caption(
        f"{completed_count} / "
        f"{total_progress} "
        f"progress selesai"
    )

    # ======================================================
    # TIMELINE
    # ======================================================

    columns_per_row = 5

    for start in range(
        0,
        total_progress,
        columns_per_row
    ):

        steps = PROGRESS_STEPS[
            start:
            start + columns_per_row
        ]

        cols = st.columns(
            columns_per_row
        )

        # --------------------------------------------------
        # STATUS
        # --------------------------------------------------

        for index, step in enumerate(
            steps
        ):

            with cols[index]:

                completed = is_completed(
                    row.get(
                        step["status_col"],
                        ""
                    )
                )

                render_status_box(
                    step["name"],
                    completed
                )

        # --------------------------------------------------
        # DATES
        # --------------------------------------------------

        for index, step in enumerate(
            steps
        ):

            with cols[index]:

                render_timeline_date(
                    "Est",
                    row.get(
                        step["estimate_col"],
                        ""
                    ),
                    selected_proposal,
                    step["estimate_col"]
                )

                render_timeline_date(
                    "Real",
                    row.get(
                        step["real_col"],
                        ""
                    ),
                    selected_proposal,
                    step["real_col"]
                )

        st.write("")
