from config import COLUMN


def apply_filters(df, filters):

    current_df = df.copy()

    # ==========================================
    # RLM
    # ==========================================

    if filters["rlm"] is not None:

        current_df = current_df[
            current_df[COLUMN["rlm"]].astype(str).str.strip()
            ==
            str(filters["rlm"]).strip()
        ]


    # ==========================================
    # LOCAM
    # ==========================================

    if filters["locam"] is not None:

        current_df = current_df[
            current_df[COLUMN["locam"]].astype(str).str.strip()
            ==
            str(filters["locam"]).strip()
        ]


    # ==========================================
    # CABANG
    # ==========================================

    if filters["cabang"] is not None:

        current_df = current_df[
            current_df[COLUMN["cabang"]].astype(str).str.strip()
            ==
            str(filters["cabang"]).strip()
        ]


    # ==========================================
    # BULAN GO
    # ==========================================

    if filters["bulan_go"] is not None:

        current_df = current_df[
            current_df[COLUMN["bulan_go"]]
            .astype(str)
            .str.strip()
            .str.upper()
            ==
            str(filters["bulan_go"])
            .strip()
            .upper()
        ]


    # ==========================================
    # PROGRES
    # ==========================================

    if filters["progres"] is not None:

        current_df = current_df[
            current_df[COLUMN["progress"]]
            .astype(str)
            .str.strip()
            ==
            str(filters["progres"])
            .strip()
        ]


    return current_df