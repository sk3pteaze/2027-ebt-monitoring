import streamlit as st


def show_proposal_summary(row):

    proposal = str(
        row.get("NAMA PROPOSAL", "-")
    ).strip()

    cabang = str(
        row.get("CAB", "-")
    ).strip()

    kode_ulok = str(
        row.get("KODE ULOK", "-")
    ).strip()

    type_toko = str(
        row.get("TYPE TOKO", "-")
    ).strip()

    tahapan = str(
        row.get("TAHAPAN", "-")
    ).strip()

    master_progress = str(
        row.get("MASTER PROGRESS", "-")
    ).strip()

    kota = str(
        row.get("KOTA/KAB", "-")
    ).strip()

    domain = str(
        row.get("DOMAIN", "-")
    ).strip()


    # =====================================================
    # HEADER
    # =====================================================

    st.markdown(
        f"### 📋 {proposal}"
    )


    # =====================================================
    # INFORMATION
    # =====================================================

    col1, col2, col3, col4 = st.columns(4)


    with col1:

        st.caption("CABANG")

        st.write(
            f"**{cabang}**"
        )


    with col2:

        st.caption("KODE ULOK")

        st.write(
            f"**{kode_ulok}**"
        )


    with col3:

        st.caption("TYPE TOKO")

        st.write(
            f"**{type_toko}**"
        )


    with col4:

        st.caption("TAHAPAN")

        st.write(
            f"**{tahapan}**"
        )


    # =====================================================
    # SECOND ROW
    # =====================================================

    col1, col2, col3 = st.columns(3)


    with col1:

        st.caption("KOTA / KAB")

        st.write(
            f"**{kota}**"
        )


    with col2:

        st.caption("DOMAIN")

        st.write(
            f"**{domain}**"
        )


    with col3:

        st.caption("CURRENT PROGRESS")

        st.write(
            f"**{master_progress}**"
        )


    st.divider()