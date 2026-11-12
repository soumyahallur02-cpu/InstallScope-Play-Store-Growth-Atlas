
from pathlib import Path
from datetime import datetime, time
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="InstallScope | Growth Atlas",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

DATA_PATH = Path(__file__).parent / "data" / "Play Store Data.csv"
TZ = ZoneInfo("Asia/Kolkata")


# ==========================================
# CATEGORY TRANSLATIONS
# ==========================================

CATEGORY_LABELS = {
    "TRAVEL_AND_LOCAL": "Voyages et lieux",
    "PRODUCTIVITY": "Productividad",
    "PHOTOGRAPHY": "写真",
    "TOOLS": "Tools",
    "PERSONALIZATION": "Personalization",
    "PARENTING": "Parenting"
}

CATEGORY_COLORS = {
    "TRAVEL_AND_LOCAL": "#4F8CFF",
    "PRODUCTIVITY": "#A78BFA",
    "PHOTOGRAPHY": "#22C99A",
    "TOOLS": "#F4A340",
    "PERSONALIZATION": "#F06F9B",
    "PARENTING": "#49C6D9"
}


# ==========================================
# ATTRACTIVE DASHBOARD CSS
# ==========================================

st.markdown("""
<style>

@import url(
'https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Manrope:wght@500;600;700;800&display=swap'
);

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background:
    radial-gradient(
        circle at 12% 0%,
        #1b3151 0%,
        #0b1220 42%,
        #080e19 100%
    );
    color: #eaf1ff;
}

.block-container {
    padding-top: 2rem;
    max-width: 1450px;
}

h1, h2, h3 {
    font-family: 'Manrope', sans-serif;
    color: #f4f7ff;
}

[data-testid="stMetric"] {
    background: linear-gradient(
        145deg,
        #172640,
        #101a2b
    );
    border: 1px solid #2b3c59;
    padding: 18px 20px;
    border-radius: 18px;
}

[data-testid="stMetricLabel"] {
    color: #aab8d0 !important;
}

[data-testid="stMetricValue"] {
    color: #f4f7ff !important;
}

section[data-testid="stSidebar"] {
    background: #0d1728;
    border-right: 1px solid #253650;
}

section[data-testid="stSidebar"] * {
    color: #eaf1ff;
}

.hero {
    padding: 28px 30px;
    border: 1px solid #2b4262;
    border-radius: 22px;
    background: linear-gradient(
        115deg,
        rgba(35,65,99,.78),
        rgba(15,28,47,.85)
    );
    margin-bottom: 25px;
}

.eyebrow {
    color: #53e5bd;
    text-transform: uppercase;
    letter-spacing: 2px;
    font-size: 11px;
    font-weight: 800;
}

.hero h1 {
    margin: 7px 0;
    font-size: 36px;
}

.hero p {
    color: #aebbd1;
}

.pill {
    display: inline-block;
    background: #173d3a;
    color: #68f0c5;
    border: 1px solid #28695d;
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 700;
    margin-right: 6px;
}

div[data-testid="stDataFrame"] {
    border: 1px solid #2b3c59;
    border-radius: 14px;
    overflow: hidden;
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# DATA CLEANING FUNCTIONS
# ==========================================

def parse_size_mb(value):

    value = str(value).strip().upper()

    if value in ["", "NAN", "VARIES WITH DEVICE"]:
        return np.nan

    try:

        if value.endswith("M"):
            return float(value[:-1])

        elif value.endswith("K"):
            return float(value[:-1]) / 1024

    except ValueError:
        return np.nan

    return np.nan


def clean_data(raw):

    df = raw.copy()

    # Convert rating
    df["Rating_num"] = pd.to_numeric(
        df["Rating"],
        errors="coerce"
    )

    # Convert reviews
    df["Reviews_num"] = pd.to_numeric(
        df["Reviews"].astype(str).str.replace(
            ",", "", regex=False
        ),
        errors="coerce"
    )

    # Convert app size to MB
    df["Size_MB"] = df["Size"].apply(parse_size_mb)

    # Convert installs
    df["Installs_num"] = pd.to_numeric(
        df["Installs"]
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("+", "", regex=False),
        errors="coerce"
    )

    # Convert last updated date
    df["Updated"] = pd.to_datetime(
        df["Last Updated"],
        errors="coerce"
    )

    # ======================================
    # REQUIRED FILTER CONDITIONS
    # ======================================

    mask = (

        # Rating at least 4.2
        (df["Rating_num"] >= 4.2)

        # App name should not contain numbers
        & (
            ~df["App"].astype(str).str.contains(
                r"\d",
                regex=True,
                na=False
            )
        )

        # Categories starting with T or P
        & df["Category"].astype(str).str.startswith(
            ("T", "P")
        )

        # Reviews greater than 1000
        & (df["Reviews_num"] > 1000)

        # App size between 20 MB and 80 MB
        & df["Size_MB"].between(
            20, 80, inclusive="both"
        )

        # Valid installs and dates
        & df["Installs_num"].notna()
        & df["Updated"].notna()
    )

    filtered = df.loc[mask].copy()

    # Extract month
    filtered["Month"] = (
        filtered["Updated"]
        .dt.to_period("M")
        .dt.to_timestamp()
    )

    # Translate category names
    filtered["Category_Display"] = (
        filtered["Category"]
        .map(CATEGORY_LABELS)
        .fillna(filtered["Category"])
    )

    return filtered


# ==========================================
# MONTHLY INSTALL CALCULATION
# ==========================================

def build_monthly(filtered):

    monthly = (
        filtered.groupby(
            ["Month", "Category"],
            as_index=False
        )["Installs_num"]
        .sum()
        .rename(
            columns={
                "Installs_num": "Monthly_Installs"
            }
        )
    )

    if monthly.empty:

        return monthly, pd.DataFrame(), []

    # Create continuous monthly index
    all_months = pd.date_range(
        monthly["Month"].min(),
        monthly["Month"].max(),
        freq="MS"
    )

    categories = sorted(
        monthly["Category"].unique()
    )

    wide = (
        monthly.pivot(
            index="Month",
            columns="Category",
            values="Monthly_Installs"
        )
        .reindex(
            index=all_months,
            columns=categories
        )
        .fillna(0)
    )

    # Calculate month-over-month growth
    growth = (
        wide.pct_change()
        .replace([np.inf, -np.inf], np.nan)
    )

    # Highlight months where ANY category
    # increased by more than 25%
    highlighted = list(
        growth.index[
            (growth > 0.25).any(axis=1)
        ]
    )

    # Calculate cumulative installs
    cumulative = wide.cumsum()

    return monthly, cumulative, highlighted


# ==========================================
# STACKED AREA CHART
# ==========================================

def make_area_chart(wide, highlighted):

    fig = go.Figure()

    for category in wide.columns:

        label = CATEGORY_LABELS.get(
            category,
            category
        )

        color = CATEGORY_COLORS.get(
            category,
            "#91A4C7"
        )

        fig.add_trace(
            go.Scatter(

                x=wide.index,

                y=wide[category],

                name=label,

                mode="lines",

                stackgroup="installs",

                line=dict(
                    width=1.5,
                    color=color
                ),

                hovertemplate=(
                    f"<b>{label}</b><br>"
                    "%{x|%b %Y}<br>"
                    "%{y:,.0f} installs"
                    "<extra></extra>"
                )
            )
        )

    # ======================================
    # GROWTH HIGHLIGHTING
    # ======================================

    for month in highlighted:

        # Highlight month with amber band
        fig.add_vrect(

            x0=month - pd.Timedelta(days=10),

            x1=month + pd.Timedelta(days=25),

            fillcolor="rgba(255,205,86,0.25)",

            line_width=0,

            layer="below"
        )

        # Add diamond growth indicator
        fig.add_trace(
            go.Scatter(

                x=[month],

                y=[1],

                yref="paper",

                mode="markers",

                marker=dict(
                    symbol="diamond",
                    size=11,
                    color="#FFD166",
                    line=dict(
                        color="#FFF1BF",
                        width=1
                    )
                ),

                name="Growth above 25%",

                legendgroup="growth",

                showlegend=(
                    month == highlighted[0]
                ),

                hovertemplate=(
                    "<b>Growth Alert</b><br>"
                    f"{month:%b %Y}<br>"
                    "At least one category grew above 25%"
                    "<extra></extra>"
                )
            )
        )

    fig.update_layout(

        height=520,

        template="plotly_dark",

        paper_bgcolor="rgba(0,0,0,0)",

        plot_bgcolor="rgba(8,15,27,0.45)",

        margin=dict(
            l=12,
            r=20,
            t=35,
            b=12
        ),

        hovermode="x unified",

        font=dict(
            family="DM Sans",
            color="#DCE7FA"
        ),

        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            x=0
        ),

        xaxis=dict(
            title="Month",
            showgrid=False,
            tickformat="%b\n%Y"
        ),

        yaxis=dict(
            title="Cumulative installs",
            gridcolor="rgba(150,170,205,.13)",
            tickformat="~s"
        )
    )

    return fig


# ==========================================
# DASHBOARD HEADER
# ==========================================



# ==========================================
# DASHBOARD HEADER - STREAMLIT NATIVE UI
# ==========================================

st.markdown("---")

st.title("📈 InstallScope | Growth Atlas")

st.subheader(
    "Google Play Store • Category Intelligence"
)

st.markdown(
    """
    Discover app category performance through intelligent
    filtering and cumulative install analytics.
    """
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.success("✓ FILTERED DATA")

with col2:
    st.info("▰ STACKED AREA")

with col3:
    st.warning("↗ GROWTH ANALYTICS")

with col4:
    st.success("◷ IST TIME GATE")

st.markdown("---")




# ==========================================
# LOAD DATASET
# ==========================================

if not DATA_PATH.exists():

    st.error(
        "Dataset not found! Please put "
        "'Play Store Data.csv' inside the data folder."
    )

    st.stop()


raw = pd.read_csv(DATA_PATH)

filtered = clean_data(raw)

monthly, wide, highlighted = build_monthly(
    filtered
)


# ==========================================
# SIDEBAR
# ==========================================

st.sidebar.markdown(
    "## ✦ Dashboard Controls"
)

st.sidebar.caption(
    "All required filters are applied automatically."
)

available = sorted(
    filtered["Category"].unique()
)

selected = st.sidebar.multiselect(

    "Select app categories",

    available,

    default=available,

    format_func=lambda x: CATEGORY_LABELS.get(
        x, x
    )
)

if selected:

    view = filtered[
        filtered["Category"].isin(selected)
    ].copy()

else:

    view = filtered.iloc[0:0].copy()


monthly_view, wide_view, highlighted_view = (
    build_monthly(view)
)


st.sidebar.markdown("---")

st.sidebar.markdown(
    "### Required Filters"
)

st.sidebar.markdown("""
- Rating ≥ 4.2
- App name contains no numbers
- Category starts with T or P
- Reviews > 1,000
- Size between 20 MB and 80 MB
""")

st.sidebar.caption(
    "Unknown and variable app sizes are excluded."
)


# ==========================================
# KPI CARDS
# ==========================================

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Matching Apps",
    f"{len(view):,}"
)

c2.metric(
    "Categories",
    f"{view['Category'].nunique():,}"
)

c3.metric(
    "Total Listed Installs",
    (
        f"{view['Installs_num'].sum()/1_000_000:,.1f}M"
        if len(view)
        else "0"
    )
)

c4.metric(
    "Growth Alert Months",
    f"{len(highlighted_view):,}"
)


# ==========================================
# TIME RESTRICTION
# ==========================================

now = datetime.now(TZ)

is_visible = (
    time(16, 0) <= now.time() < time(18, 0)
)


st.markdown("## 📊 Monthly Install Accumulation")

st.caption(
    "The stacked area visualization is available "
    "only between 4 PM and 6 PM IST."
)


# ==========================================
# DISPLAY CHART ONLY DURING TIME WINDOW
# ==========================================

if is_visible:

    if wide_view.empty:

        st.warning(
            "No matching applications. "
            "Please select at least one category."
        )

    else:

        fig = make_area_chart(
            wide_view,
            highlighted_view
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={
                "displayModeBar": False
            }
        )

        st.markdown(
            "🟡 **Growth Alert:** Yellow highlighted "
            "months indicate more than 25% growth "
            "in at least one category."
        )

else:

    st.info(
        f"""
        🔒 **Chart Currently Locked**

        The visualization is available daily from
        **4:00 PM to 6:00 PM IST**.

        Current IST time:
        **{now.strftime('%I:%M:%S %p')}**

        Please revisit during the permitted time window.
        """
    )


# ==========================================
# FILTERED APP EXPLORER
# ==========================================

st.markdown("---")

left, right = st.columns([1.2, 1])


with left:

    st.markdown(
        "## 📱 Filtered App Explorer"
    )

    display_cols = [
        "App",
        "Category_Display",
        "Rating_num",
        "Reviews_num",
        "Size_MB",
        "Installs_num",
        "Updated"
    ]

    table = view[display_cols].rename(

        columns={

            "Category_Display": "Category",

            "Rating_num": "Rating",

            "Reviews_num": "Reviews",

            "Size_MB": "Size (MB)",

            "Installs_num": "Installs",

            "Updated": "Last Updated"
        }

    ).sort_values(
        "Installs",
        ascending=False
    ) if len(view) else pd.DataFrame(
        columns=display_cols
    )

    st.dataframe(

        table,

        use_container_width=True,

        hide_index=True,

        height=370
    )


# ==========================================
# CATEGORY INSTALL COMPARISON
# ==========================================

with right:

    st.markdown(
        "## 🏆 Category Install Comparison"
    )

    if len(view):

        mix = (
            view.groupby("Category_Display")[
                "Installs_num"
            ]
            .sum()
            .sort_values()
        )

        # Match bar colors to original categories
        category_color_map = {
            CATEGORY_LABELS.get(category, category):
            CATEGORY_COLORS.get(category, "#91A4C7")
            for category in view["Category"].unique()
        }

        fig_bar = go.Figure(

            go.Bar(

                x=mix.values,

                y=mix.index,

                orientation="h",

                marker_color=[
                    category_color_map.get(
                        name, "#91A4C7"
                    )
                    for name in mix.index
                ],

                hovertemplate=(
                    "%{y}<br>"
                    "%{x:,.0f} installs"
                    "<extra></extra>"
                )
            )
        )

        fig_bar.update_layout(

            height=370,

            template="plotly_dark",

            paper_bgcolor="rgba(0,0,0,0)",

            plot_bgcolor="rgba(0,0,0,0)",

            margin=dict(
                l=4,
                r=8,
                t=10,
                b=10
            ),

            xaxis=dict(
                showgrid=False,
                title="Installs"
            ),

            yaxis=dict(
                title=""
            )
        )

        st.plotly_chart(
            fig_bar,
            use_container_width=True,
            config={
                "displayModeBar": False
            }
        )

    else:

        st.caption(
            "Select categories to view the comparison."
        )


# ==========================================
# METHODOLOGY
# ==========================================

st.markdown("---")

st.markdown(
    "## 🧠 Project Methodology"
)

st.markdown("""
**1. Data Cleaning**

Unnecessary symbols are removed from ratings,
reviews, installs and app sizes.

**2. Data Filtering**

Only applications satisfying all five required
conditions are selected.

**3. Category Grouping**

Applications are grouped according to their
category and last-updated month.

**4. Cumulative Install Calculation**

Monthly category install totals are accumulated
over time.

**5. Growth Detection**

Month-over-month growth is calculated for each
category. Months with growth above 25% are highlighted.

**6. Time-Based Visibility**

The stacked area chart is displayed only between
4 PM and 6 PM IST.
""")


# ==========================================
# FOOTER
# ==========================================

st.markdown("---")

st.caption(
    f"InstallScope Growth Atlas | "
    f"Source records: {len(raw):,} | "
    f"Filtered records: {len(filtered):,} | "
    f"Timezone: Asia/Kolkata"
)

st.caption(
    "Built with Python • Streamlit • Pandas • Plotly"
)
