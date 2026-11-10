import streamlit as st

from config import COLUMN


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
# PROGRESS FILTERS
# ==========================================================

def progress_filters(df):

    current_df = df.copy()

    col1, col2, col3, col4, col5, col6 = st.columns(6)


    # ==========================================
    # BULAN KPI
    # Menggantikan SM
    # ==========================================

    with col1:

        bulan_sekarang = MONTHS[
            __import__("datetime").datetime.now().month - 1
        ]

        bulan_kpi = st.selectbox(

            "BULAN KPI",

            options=MONTHS,

            index=MONTHS.index(
                bulan_sekarang
            ),

            key="bulan_kpi_filter"

        )


    # ==========================================
    # RLM
    # ==========================================

    with col2:

        rlm = st.selectbox(

            "RLM",

            options=sorted(

                current_df[
                    COLUMN["rlm"]
                ]
                .dropna()
                .astype(str)
                .str.strip()
                .unique()

            ),

            index=None,

            placeholder="RLM",

            key="rlm_filter"

        )

    if rlm is not None:

        current_df = current_df[

            current_df[
                COLUMN["rlm"]
            ]
            .astype(str)
            .str.strip()
            ==
            str(rlm).strip()

        ]


    # ==========================================
    # LOCAM
    # ==========================================

    with col3:

        locam = st.selectbox(

            "LOCAM",

            options=sorted(

                current_df[
                    COLUMN["locam"]
                ]
                .dropna()
                .astype(str)
                .str.strip()
                .unique()

            ),

            index=None,

            placeholder="LOCAM",

            key="locam_filter"

        )

    if locam is not None:

        current_df = current_df[

            current_df[
                COLUMN["locam"]
            ]
            .astype(str)
            .str.strip()
            ==
            str(locam).strip()

        ]


    # ==========================================
    # CABANG
    # ==========================================

    with col4:

        cabang = st.selectbox(

            "CABANG",

            options=sorted(

                current_df[
                    COLUMN["cabang"]
                ]
                .dropna()
                .astype(str)
                .str.strip()
                .unique()

            ),

            index=None,

            placeholder="CABANG",

            key="cabang_filter"

        )

    if cabang is not None:

        current_df = current_df[

            current_df[
                COLUMN["cabang"]
            ]
            .astype(str)
            .str.strip()
            ==
            str(cabang).strip()

        ]


    # ==========================================
    # BULAN GO
    # ==========================================

    with col5:

        available_bulan = (

            current_df[
                "BULAN GO"
            ]

            .dropna()

            .astype(str)

            .str.strip()

            .str.upper()

            .unique()

        )

        bulan_options = [

            bulan

            for bulan in MONTHS

            if bulan in available_bulan

        ]

        bulan_go = st.selectbox(

            "BULAN GO",

            options=bulan_options,

            index=None,

            placeholder="BULAN GO",

            key="bulan_go_filter"

        )

    if bulan_go is not None:

        current_df = current_df[

            current_df[
                "BULAN GO"
            ]
            .astype(str)
            .str.strip()
            .str.upper()
            ==
            str(bulan_go).strip().upper()

        ]


    # ==========================================
    # PROGRES
    # ==========================================

    with col6:

        progres = st.selectbox(

            "PROGRES",

            options=sorted(

                current_df[
                    COLUMN["progress"]
                ]
                .dropna()
                .astype(str)
                .str.strip()
                .unique()

            ),

            index=None,

            placeholder="PROGRES",

            key="progres_filter"

        )


    # ==========================================
    # RETURN FILTER
    # ==========================================

    return {

        "bulan_kpi": bulan_kpi,

        "rlm": rlm,

        "locam": locam,

        "cabang": cabang,

        "bulan_go": bulan_go,

        "progres": progres

    }