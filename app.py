
from pathlib import Path
from datetime import datetime, time
from zoneinfo import ZoneInfo
import re

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="InstallScope | Growth Atlas",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "Play Store Data.csv"
IST = ZoneInfo("Asia/Kolkata")


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background:
            radial-gradient(circle at 10% 0%, #142d38 0%, transparent 32%),
            linear-gradient(135deg, #07131c 0%, #0b1b27 55%, #101d2a 100%);
        color: #f1f5f9;
    }

    [data-testid="stSidebar"] {
        background: #101f2b;
        border-right: 1px solid rgba(148, 163, 184, 0.18);
    }

    [data-testid="stSidebar"] * {
        color: #e5edf5 !important;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #55f0c1 !important;
    }

    [data-testid="stMetric"] {
        background: rgba(25, 49, 62, 0.75);
        border: 1px solid rgba(85, 240, 193, 0.18);
        padding: 15px;
        border-radius: 13px;
    }

    [data-testid="stMetricLabel"] {
        color: #a8bac8 !important;
    }

    [data-testid="stMetricValue"] {
        color: #55f0c1 !important;
        font-weight: 800;
    }

    .main-title {
        font-size: 42px;
        font-weight: 900;
        color: #f8fafc;
        letter-spacing: -1.5px;
        margin-bottom: 5px;
    }

    .main-title span {
        color: #43e0b3;
    }

    .subtitle {
        color: #a8bac8;
        font-size: 15px;
        margin-bottom: 22px;
    }

    .eyebrow {
        color: #55f0c1;
        font-size: 12px;
        font-weight: 800;
        letter-spacing: 2px;
        margin-bottom: 10px;
    }

    .section-heading {
        color: #f1f5f9;
        font-size: 21px;
        font-weight: 800;
        margin-top: 18px;
        margin-bottom: 8px;
    }

    .info-card {
        background: rgba(25, 49, 62, 0.72);
        border: 1px solid rgba(85, 240, 193, 0.18);
        border-radius: 14px;
        padding: 18px;
        margin-bottom: 12px;
    }

    .info-card p {
        color: #b9c8d4;
        margin-bottom: 0;
        font-size: 13px;
    }

    .info-card h3 {
        color: #55f0c1;
        margin-top: 0;
    }

    .pill {
        display: inline-block;
        background: rgba(67, 224, 179, 0.12);
        color: #55f0c1;
        border: 1px solid rgba(67, 224, 179, 0.35);
        border-radius: 20px;
        padding: 5px 12px;
        font-size: 11px;
        font-weight: 700;
        margin-right: 6px;
        margin-bottom: 6px;
    }

    div[data-testid="stDownloadButton"] button {
        background: #43e0b3;
        color: #07131c;
        border: none;
        font-weight: 800;
        border-radius: 9px;
    }

    div[data-testid="stDownloadButton"] button:hover {
        background: #55f0c1;
        color: #07131c;
    }

    .footer {
        text-align: center;
        color: #8194a5;
        font-size: 12px;
        padding: 25px 0 10px 0;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# DATA LOADING
# ============================================================

@st.cache_data(show_spinner="Loading Google Play Store dataset...")
def load_data(file_path, file_modified):

    df = pd.read_csv(file_path)

    required_columns = [
        "App",
        "Category",
        "Rating",
        "Reviews",
        "Size",
        "Installs",
        "Last Updated"
    ]

    missing_columns = [
        col for col in required_columns if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {', '.join(missing_columns)}"
        )

    df["App"] = df["App"].astype(str).str.strip()
    df["Category"] = df["Category"].astype(str).str.strip()

    df["Rating"] = pd.to_numeric(
        df["Rating"], errors="coerce"
    )

    df["Reviews"] = pd.to_numeric(
        df["Reviews"].astype(str).str.replace(",", "", regex=False),
        errors="coerce"
    )

    df["Installs"] = pd.to_numeric(
        df["Installs"]
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("+", "", regex=False),
        errors="coerce"
    )

    df["Last Updated"] = pd.to_datetime(
        df["Last Updated"],
        errors="coerce"
    )

    df["Size_MB"] = df["Size"].apply(parse_size_mb)

    df = df.dropna(
        subset=["App", "Category", "Rating", "Reviews",
                "Installs", "Last Updated"]
    )

    return df


# ============================================================
# SIZE CONVERSION
# ============================================================

def parse_size_mb(value):

    if pd.isna(value):
        return np.nan

    value = str(value).strip().upper()

    if value in ["", "NAN", "VARIES WITH DEVICE"]:
        return np.nan

    match = re.search(r"(\d+(?:\.\d+)?)\s*([A-Z]+)?", value)

    if not match:
        return np.nan

    number = float(match.group(1))
    unit = match.group(2) or "M"

    if unit == "G":
        return number * 1024

    if unit == "GB":
        return number * 1024

    if unit in ["M", "MB"]:
        return number

    if unit in ["K", "KB"]:
        return number / 1024

    if unit == "B":
        return number / (1024 * 1024)

    return number


# ============================================================
# FILTERING
# ============================================================

def apply_project_filters(df):

    diagnostics = []

    diagnostics.append(("Original dataset", len(df)))

    # Filter 1: Rating >= 4.2
    filtered = df[df["Rating"] >= 4.2].copy()

    diagnostics.append(("Rating >= 4.2", len(filtered)))

    # Filter 2: App name should not contain numbers
    filtered = filtered[
        ~filtered["App"].str.contains(r"\d", regex=True, na=False)
    ].copy()

    diagnostics.append(("App names without numbers", len(filtered)))

    # Filter 3: Category starts with T or P
    filtered = filtered[
        filtered["Category"].str.upper().str.startswith(("T", "P"))
    ].copy()

    diagnostics.append(("Category starts with T/P", len(filtered)))

    # Filter 4: Reviews > 1,000
    filtered = filtered[
        filtered["Reviews"] > 1000
    ].copy()

    diagnostics.append(("Reviews > 1,000", len(filtered)))

    # Filter 5: App size between 20 MB and 80 MB
    filtered = filtered[
        filtered["Size_MB"].between(20, 80, inclusive="both")
    ].copy()

    diagnostics.append(("App size 20–80 MB", len(filtered)))

    return filtered, diagnostics


# ============================================================
# CATEGORY TRANSLATIONS
# ============================================================

CATEGORY_TRANSLATIONS = {
    "TRAVEL_AND_LOCAL": "Voyages et lieux",
    "PRODUCTIVITY": "Productividad",
    "PHOTOGRAPHY": "写真"
}


def translate_category(category):

    return CATEGORY_TRANSLATIONS.get(
        str(category).upper(),
        category
    )


# ============================================================
# MONTHLY INSTALL ANALYSIS
# ============================================================

def prepare_monthly_data(df):

    if df.empty:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    working = df.copy()

    working["Month"] = (
        working["Last Updated"]
        .dt.to_period("M")
        .dt.to_timestamp()
    )

    monthly = (
        working.groupby(["Month", "Category"])["Installs"]
        .sum()
        .reset_index()
    )

    monthly_wide = monthly.pivot(
        index="Month",
        columns="Category",
        values="Installs"
    ).fillna(0)

    if monthly_wide.empty:
        return monthly, monthly_wide, monthly_wide

    # Create a continuous monthly timeline
    all_months = pd.date_range(
        start=monthly_wide.index.min(),
        end=monthly_wide.index.max(),
        freq="MS"
    )

    monthly_wide = monthly_wide.reindex(
        all_months,
        fill_value=0
    )

    monthly_wide.index.name = "Month"

    # Month-over-month growth
    growth = monthly_wide.pct_change(
        fill_method=None
    ).replace([np.inf, -np.inf], np.nan)

    # Cumulative installs
    cumulative = monthly_wide.cumsum()

    return monthly, monthly_wide, growth, cumulative


# ============================================================
# STACKED AREA CHART
# ============================================================

def create_area_chart(monthly_wide, growth, cumulative):

    fig = go.Figure()

    if monthly_wide.empty:
        return fig

    categories = list(monthly_wide.columns)

    color_palette = [
        "#43e0b3",
        "#5aa9e6",
        "#f6bd60",
        "#c77dff",
        "#ff7b9c",
        "#7bdff2",
        "#b8f2a1",
        "#f28482",
        "#a0c4ff",
        "#ffc6ff"
    ]

    # Stacked cumulative area chart
    for index, category in enumerate(categories):

        translated_name = translate_category(category)

        fig.add_trace(
            go.Scatter(
                x=cumulative.index,
                y=cumulative[category],
                mode="lines",
                name=translated_name,
                stackgroup="one",
                line=dict(
                    width=1.5,
                    color=color_palette[index % len(color_palette)]
                ),
                hovertemplate=(
                    "<b>%{fullData.name}</b><br>"
                    "Month: %{x|%b %Y}<br>"
                    "Cumulative installs: %{y:,.0f}"
                    "<extra></extra>"
                )
            )
        )

    # Highlight months where any category has >25% growth
    growth_values = growth.copy()

    high_growth_months = growth_values.index[
        growth_values.gt(0.25).any(axis=1)
    ]

    for month in high_growth_months:

        fig.add_vrect(
            x0=month,
            x1=month + pd.offsets.MonthBegin(1),
            fillcolor="rgba(246, 189, 96, 0.13)",
            line_width=0,
            layer="below"
        )

    # Add markers for high-growth months
    marker_x = []
    marker_y = []

    for month in high_growth_months:

        if month in cumulative.index:
            marker_x.append(month)
            marker_y.append(
                cumulative.loc[month].sum()
            )

    if marker_x:

        fig.add_trace(
            go.Scatter(
                x=marker_x,
                y=marker_y,
                mode="markers",
                name="Growth above 25%",
                marker=dict(
                    symbol="diamond",
                    size=10,
                    color="#f6bd60",
                    line=dict(width=1, color="#ffffff")
                ),
                hovertemplate=(
                    "<b>High growth month</b><br>"
                    "%{x|%b %Y}<br>"
                    "Cumulative installs: %{y:,.0f}"
                    "<extra></extra>"
                )
            )
        )

    fig.update_layout(
        height=520,
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        title=dict(
            text="Cumulative Installs by Category",
            font=dict(size=21, color="#f1f5f9")
        ),
        xaxis=dict(
            title="Month",
            showgrid=True,
            gridcolor="rgba(148,163,184,0.12)",
            tickformat="%b %Y"
        ),
        yaxis=dict(
            title="Cumulative Installs",
            showgrid=True,
            gridcolor="rgba(148,163,184,0.12)",
            tickformat="~s"
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0
        ),
        hovermode="x unified",
        margin=dict(l=15, r=15, t=90, b=15)
    )

    return fig


# ============================================================
# LOAD DATA
# ============================================================

if not DATA_PATH.exists():

    st.error(
        "Dataset not found. Please check that your CSV file is inside "
        "the data folder."
    )

    st.code(
        "Your project folder should look like this:\n\n"
        "PlayStore_Install_Insights/\n"
        "│\n"
        "├── app.py\n"
        "├── requirements.txt\n"
        "└── data/\n"
        "    └── Play Store Data.csv"
    )

    st.stop()


try:

    file_modified = DATA_PATH.stat().st_mtime

    df = load_data(
        str(DATA_PATH),
        file_modified
    )

except Exception as error:

    st.error(f"Unable to load dataset: {error}")
    st.stop()


# ============================================================
# APPLY FILTERS
# ============================================================

filtered_df, diagnostics = apply_project_filters(df)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div class="eyebrow">GOOGLE PLAY STORE</div>
        <h2 style="color:#55f0c1 !important;">
            InstallScope
        </h2>
        <p style="color:#a8bac8 !important;">
            Growth Atlas | Category Intelligence
        </p>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")

    st.markdown("### Dashboard Overview")

    st.write("Explore filtered Google Play Store app data.")

    st.markdown("---")

    st.markdown("### Filter Diagnostics")

    # Corrected diagnostics: native Streamlit metrics.
    # This prevents raw HTML from appearing in the sidebar.

    for label, count in diagnostics:

        st.metric(
            label=label,
            value=f"{count:,} records"
        )

    st.markdown("---")

    st.markdown("### Active Filters")

    st.markdown(
        """
        <span class="pill">Rating ≥ 4.2</span>
        <span class="pill">No numbers in app name</span>
        <span class="pill">Category T / P</span>
        <span class="pill">Reviews > 1,000</span>
        <span class="pill">Size 20–80 MB</span>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")

    st.caption("Data source: Google Play Store dataset")


# ============================================================
# MAIN HEADER
# ============================================================

st.markdown(
    """
    <div class="eyebrow">
        GOOGLE PLAY STORE • CATEGORY INTELLIGENCE
    </div>

    <div class="main-title">
        InstallScope <span>/</span> Growth Atlas
    </div>

    <div class="subtitle">
        Discover app category performance through
        intelligent filtering and cumulative install analytics.
    </div>

    <span class="pill">FILTERED DATA ANALYSIS</span>
    <span class="pill">CATEGORY PERFORMANCE</span>
    <span class="pill">INSTALL GROWTH</span>
    """,
    unsafe_allow_html=True
)


# ============================================================
# KPI CARDS
# ============================================================

total_apps = len(filtered_df)

total_installs = (
    filtered_df["Installs"].sum()
    if not filtered_df.empty else 0
)

average_rating = (
    filtered_df["Rating"].mean()
    if not filtered_df.empty else 0
)

total_categories = (
    filtered_df["Category"].nunique()
    if not filtered_df.empty else 0
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Filtered Apps",
        f"{total_apps:,}"
    )

with col2:
    st.metric(
        "Total Installs",
        f"{total_installs:,.0f}"
    )

with col3:
    st.metric(
        "Average Rating",
        f"{average_rating:.2f} / 5"
    )

with col4:
    st.metric(
        "Categories",
        f"{total_categories:,}"
    )


# ============================================================
# CATEGORY FILTER
# ============================================================

st.markdown(
    '<div class="section-heading">Category Explorer</div>',
    unsafe_allow_html=True
)

if not filtered_df.empty:

    available_categories = sorted(
        filtered_df["Category"].dropna().unique().tolist()
    )

    selected_categories = st.multiselect(
        "Select categories to display",
        options=available_categories,
        default=available_categories,
        format_func=translate_category
    )

    display_df = filtered_df[
        filtered_df["Category"].isin(selected_categories)
    ].copy()

else:

    display_df = filtered_df.copy()


# ============================================================
# CHART AND TIME RESTRICTION
# ============================================================

st.markdown(
    '<div class="section-heading">Install Growth Atlas</div>',
    unsafe_allow_html=True
)

st.caption(
    "The cumulative install chart is available daily between "
    "4:00 PM and 6:00 PM Indian Standard Time (IST). "
    "Amber highlights indicate months with more than 25% "
    "month-over-month growth in at least one category."
)


@st.fragment(run_every="60s")
def render_growth_chart(data):

    current_time = datetime.now(IST).time()

    start_time = time(16, 0)
    end_time = time(18, 0)

    if start_time <= current_time < end_time:

        if data.empty:

            st.warning(
                "No data available for the selected categories."
            )

        else:

            monthly, monthly_wide, growth, cumulative = (
                prepare_monthly_data(data)
            )

            if not monthly_wide.empty:

                chart = create_area_chart(
                    monthly_wide,
                    growth,
                    cumulative
                )

                st.plotly_chart(
                    chart,
                    use_container_width=True
                )

                high_growth_months = growth.index[
                    growth.gt(0.25).any(axis=1)
                ]

                st.info(
                    f"Months with growth above 25%: "
                    f"{len(high_growth_months)}"
                )

                if len(high_growth_months) > 0:

                    growth_month_names = [
                        month.strftime("%b %Y")
                        for month in high_growth_months
                    ]

                    st.write(
                        "**High-growth months:** "
                        + ", ".join(growth_month_names)
                    )

            else:

                st.warning(
                    "Monthly install data is not available."
                )

    else:

        st.warning(
            "The Install Growth Atlas chart is currently locked."
        )

        st.info(
            "Chart availability: 4:00 PM – 6:00 PM IST every day."
        )

        st.write(
            f"Current IST time: "
            f"{datetime.now(IST).strftime('%I:%M:%S %p')}"
        )


render_growth_chart(display_df)


# ============================================================
# CATEGORY COMPARISON
# ============================================================

st.markdown(
    '<div class="section-heading">Category Comparison</div>',
    unsafe_allow_html=True
)

if not display_df.empty:

    category_summary = (
        display_df.groupby("Category")
        .agg(
            Apps=("App", "count"),
            Total_Installs=("Installs", "sum"),
            Average_Rating=("Rating", "mean")
        )
        .reset_index()
        .sort_values("Total_Installs", ascending=False)
    )

    category_summary["Category"] = (
        category_summary["Category"].apply(translate_category)
    )

    category_col1, category_col2 = st.columns(2)

    with category_col1:

        comparison_chart = go.Figure()

        comparison_chart.add_trace(
            go.Bar(
                x=category_summary["Category"],
                y=category_summary["Total_Installs"],
                marker_color="#43e0b3",
                name="Total Installs",
                hovertemplate=(
                    "%{x}<br>"
                    "Installs: %{y:,.0f}"
                    "<extra></extra>"
                )
            )
        )

        comparison_chart.update_layout(
            title="Total Installs by Category",
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=390,
            xaxis_title="Category",
            yaxis_title="Total Installs",
            margin=dict(l=10, r=10, t=60, b=10)
        )

        st.plotly_chart(
            comparison_chart,
            use_container_width=True
        )

    with category_col2:

        rating_chart = go.Figure()

        rating_chart.add_trace(
            go.Bar(
                x=category_summary["Category"],
                y=category_summary["Average_Rating"],
                marker_color="#5aa9e6",
                name="Average Rating",
                hovertemplate=(
                    "%{x}<br>"
                    "Average rating: %{y:.2f}"
                    "<extra></extra>"
                )
            )
        )

        rating_chart.update_layout(
            title="Average Rating by Category",
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=390,
            xaxis_title="Category",
            yaxis_title="Average Rating",
            yaxis_range=[0, 5],
            margin=dict(l=10, r=10, t=60, b=10)
        )

        st.plotly_chart(
            rating_chart,
            use_container_width=True
        )

    with st.expander("View Category Summary Table"):

        st.dataframe(
            category_summary,
            use_container_width=True,
            hide_index=True
        )

else:

    st.info("No category data available for comparison.")


# ============================================================
# APP EXPLORER
# ============================================================

st.markdown(
    '<div class="section-heading">App Explorer</div>',
    unsafe_allow_html=True
)

if not display_df.empty:

    search_text = st.text_input(
        "Search app by name",
        placeholder="Enter an app name..."
    )

    explorer_df = display_df.copy()

    if search_text:

        explorer_df = explorer_df[
            explorer_df["App"].str.contains(
                search_text,
                case=False,
                na=False
            )
        ]

    explorer_columns = [
        "App",
        "Category",
        "Rating",
        "Reviews",
        "Size",
        "Installs",
        "Last Updated"
    ]

    st.dataframe(
        explorer_df[explorer_columns].sort_values(
            "Installs",
            ascending=False
        ),
        use_container_width=True,
        hide_index=True
    )

    st.caption(
        f"Displaying {len(explorer_df):,} matching apps."
    )

    csv_data = explorer_df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="Download Filtered App Data (CSV)",
        data=csv_data,
        file_name="InstallScope_Filtered_Data.csv",
        mime="text/csv"
    )

else:

    st.info(
        "No apps match the selected category filters."
    )


# ============================================================
# METHODOLOGY
# ============================================================

st.markdown(
    '<div class="section-heading">Methodology</div>',
    unsafe_allow_html=True
)

method_col1, method_col2 = st.columns(2)

with method_col1:

    st.markdown(
        """
        <div class="info-card">
            <h3>Data Filtering</h3>
            <p>
                The dataset is processed using five conditions:
                rating of at least 4.2, app names without numbers,
                categories beginning with T or P, more than 1,000
                reviews, and app size between 20 MB and 80 MB.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

with method_col2:

    st.markdown(
        """
        <div class="info-card">
            <h3>Growth Analysis</h3>
            <p>
                Monthly installs are aggregated by category.
                Cumulative installs are calculated over time.
                Months with more than 25% month-over-month growth
                in at least one category are highlighted.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">
        <b>InstallScope | Growth Atlas</b><br>
        Google Play Store Category Intelligence Dashboard<br>
        Built with Python • Streamlit • Pandas • Plotly
    </div>
    """,
    unsafe_allow_html=True
)
