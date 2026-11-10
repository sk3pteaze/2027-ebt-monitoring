import plotly.express as px

from config import COLUMN

# ==========================
# COLORS
# ==========================

COLORS = {
    "TAHAP 1": "#F4B400",   # Kuning
    "TAHAP 2": "#34A853",   # Hijau
    "GO": "#4285F4"         # Biru
}


# ==========================
# PIE CHART TAHAPAN
# ==========================

def pie_tahapan(df):

    chart_df = (
        df.groupby(COLUMN["tahapan"])
        .size()
        .reset_index(name="Jumlah Proposal")
    )

    fig = px.pie(
        chart_df,
        names=COLUMN["tahapan"],
        values="Jumlah Proposal",
        hole=0.55,
        color=COLUMN["tahapan"],
        color_discrete_map=COLORS
    )

    fig.update_traces(
        textposition="inside",
        textinfo="label+percent",
        hovertemplate=
        "<b>%{label}</b><br>"
        "Proposal : %{value}<br>"
        "Persentase : %{percent}<extra></extra>",
        marker=dict(
            line=dict(
                width=0
            )
        )
    )

    fig.update_layout(
        title=dict(
            text="Distribusi Tahapan",
            x=0.5
        ),
        legend_title="Tahapan",
        legend=dict(
            orientation="v",
            y=0.5,
            yanchor="middle",
            x=1.02
        ),
        height=450,
        margin=dict(
            l=20,
            r=20,
            t=60,
            b=20
        )
    )

    return fig


# ==========================
# BAR CHART PIC
# ==========================

def proposal_pic_dept(df):

    chart_df = (
        df.groupby(COLUMN["pic"])
        .size()
        .reset_index(name="Jumlah Proposal")
        .sort_values("Jumlah Proposal", ascending=False)
        .head(10)
        .sort_values("Jumlah Proposal", ascending=True)
    )

    fig = px.bar(
        chart_df,
        x="Jumlah Proposal",
        y=COLUMN["pic"],
        orientation="h",
        text="Jumlah Proposal"
    )

    fig.update_traces(
        marker_color="#4285F4",
        textposition="outside",
        hovertemplate=
        "<b>%{y}</b><br>"
        "Jumlah Proposal : %{x}<extra></extra>"
    )

    fig.update_layout(
        title=dict(
            text="PIC Department",
            x=0.5
        ),
        xaxis_title="Jumlah Proposal",
        yaxis_title="",
        plot_bgcolor="white",
        paper_bgcolor="white",
        height=450,
        margin=dict(
            l=20,
            r=20,
            t=60,
            b=20
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor="#E5E7EB",
            zeroline=False
        ),
        yaxis=dict(
            showgrid=False
        )
    )

    return fig