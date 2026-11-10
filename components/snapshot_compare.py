import pandas as pd

from data.log_loader import load_log


def normalize_text(value):

    if value is None or pd.isna(value):
        return ""

    return str(value).strip()


def normalize_date(value):

    if value is None or pd.isna(value):
        return None

    parsed = pd.to_datetime(
        value,
        errors="coerce"
    )

    if pd.isna(parsed):
        return None

    return parsed.date()


def get_snapshot_dates():

    log_df = load_log()

    if log_df.empty:
        return []

    if "Snapshot Date" not in log_df.columns:
        return []

    dates = pd.to_datetime(
        log_df["Snapshot Date"],
        errors="coerce"
    )

    dates = (
        dates
        .dropna()
        .dt.date
        .drop_duplicates()
        .sort_values()
        .tolist()
    )

    return dates


def compare_snapshots(
    selected_proposal,
    old_date,
    new_date
):

    log_df = load_log()

    if log_df.empty:
        return pd.DataFrame()

    required_columns = [
        "Snapshot Date",
        "Proposal",
        "Field",
        "Old Value",
        "New Value"
    ]

    for column in required_columns:

        if column not in log_df.columns:
            return pd.DataFrame()

    # ==================================================
    # NORMALIZE SNAPSHOT DATE
    # ==================================================

    log_df["_snapshot_date"] = pd.to_datetime(
        log_df["Snapshot Date"],
        errors="coerce"
    ).dt.date

    old_date = normalize_date(old_date)
    new_date = normalize_date(new_date)

    if old_date is None or new_date is None:
        return pd.DataFrame()

    # ==================================================
    # FILTER PROPOSAL
    # ==================================================

    proposal_df = log_df[
        log_df["Proposal"]
        .astype(str)
        .str.strip()
        .str.upper()
        ==
        str(selected_proposal)
        .strip()
        .upper()
    ].copy()

    if proposal_df.empty:
        return pd.DataFrame()

    # ==================================================
    # FILTER 2 SNAPSHOT
    # ==================================================

    snapshot_df = proposal_df[
        proposal_df["_snapshot_date"].isin(
            [old_date, new_date]
        )
    ].copy()

    if snapshot_df.empty:
        return pd.DataFrame()

    # ==================================================
    # KUNCI COMPARE
    # ==================================================

    # ULOK digunakan jika tersedia.
    # Kalau kosong, Proposal + Field tetap digunakan.

    if "ULOK" in snapshot_df.columns:

        snapshot_df["_ulok"] = (
            snapshot_df["ULOK"]
            .astype(str)
            .str.strip()
        )

    else:

        snapshot_df["_ulok"] = ""

    snapshot_df["_field"] = (
        snapshot_df["Field"]
        .astype(str)
        .str.strip()
        .str.upper()
        .str.replace(
            r"\s+",
            " ",
            regex=True
        )
    )

    # ==================================================
    # AMBIL RECORD TERAKHIR PER FIELD
    # ==================================================

    if "Timestamp" in snapshot_df.columns:

        snapshot_df["_timestamp"] = pd.to_datetime(
            snapshot_df["Timestamp"],
            errors="coerce"
        )

        snapshot_df = snapshot_df.sort_values(
            "_timestamp"
        )

    # ==================================================
    # OLD SNAPSHOT
    # ==================================================

    old_df = snapshot_df[
        snapshot_df["_snapshot_date"]
        == old_date
    ].copy()

    # ==================================================
    # NEW SNAPSHOT
    # ==================================================

    new_df = snapshot_df[
        snapshot_df["_snapshot_date"]
        == new_date
    ].copy()

    if old_df.empty or new_df.empty:

        return pd.DataFrame()

    # ==================================================
    # LAST RECORD PER FIELD
    # ==================================================

    old_df = old_df.drop_duplicates(
        subset=[
            "_ulok",
            "_field"
        ],
        keep="last"
    )

    new_df = new_df.drop_duplicates(
        subset=[
            "_ulok",
            "_field"
        ],
        keep="last"
    )

    # ==================================================
    # RENAME VALUE
    # ==================================================

    old_df = old_df[
        [
            "_ulok",
            "_field",
            "Old Value",
            "New Value"
        ]
    ].copy()

    new_df = new_df[
        [
            "_ulok",
            "_field",
            "Old Value",
            "New Value"
        ]
    ].copy()

    old_df = old_df.rename(
        columns={
            "New Value": "old_snapshot_value"
        }
    )

    new_df = new_df.rename(
        columns={
            "New Value": "new_snapshot_value"
        }
    )

    # ==================================================
    # MERGE OLD VS NEW
    # ==================================================

    comparison = pd.merge(
        old_df[
            [
                "_ulok",
                "_field",
                "old_snapshot_value"
            ]
        ],
        new_df[
            [
                "_ulok",
                "_field",
                "new_snapshot_value"
            ]
        ],
        on=[
            "_ulok",
            "_field"
        ],
        how="outer"
    )

    comparison[
        "old_snapshot_value"
    ] = comparison[
        "old_snapshot_value"
    ].fillna("")

    comparison[
        "new_snapshot_value"
    ] = comparison[
        "new_snapshot_value"
    ].fillna("")

    # ==================================================
    # HANYA YANG BERBEDA
    # ==================================================

    comparison = comparison[
        comparison["old_snapshot_value"]
        .astype(str)
        .str.strip()
        !=
        comparison["new_snapshot_value"]
        .astype(str)
        .str.strip()
    ].copy()

    # ==================================================
    # FIELD ASLI
    # ==================================================

    comparison["Field"] = (
        comparison["_field"]
    )

    # ==================================================
    # DAY DIFF
    # ==================================================

    comparison["DayDiff"] = None

    for index, row in comparison.iterrows():

        old_value = row[
            "old_snapshot_value"
        ]

        new_value = row[
            "new_snapshot_value"
        ]

        old_date_value = pd.to_datetime(
            old_value,
            errors="coerce"
        )

        new_date_value = pd.to_datetime(
            new_value,
            errors="coerce"
        )

        if (
            pd.notna(old_date_value)
            and
            pd.notna(new_date_value)
        ):

            comparison.loc[
                index,
                "DayDiff"
            ] = (
                new_date_value.date()
                -
                old_date_value.date()
            ).days

    return comparison.reset_index(
        drop=True
    )