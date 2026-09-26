import requests
import pandas as pd
import plotly.express as px
import streamlit as st


# ============================================================
# Page Configuration
# ============================================================

st.set_page_config(
    page_title="AirShift",
    page_icon="🌬️",
    layout="wide",
)


# ============================================================
# Configuration
# ============================================================

API_URL = "http://127.0.0.1:8000"

STATIONS = [
    "Aotizhongxin",
    "Changping",
    "Dingling",
    "Dongsi",
    "Guanyuan",
    "Gucheng",
    "Huairou",
    "Nongzhanguan",
    "Shunyi",
    "Tiantan",
    "Wanliu",
    "Wanshouxigong",
]


# ============================================================
# Custom CSS
# ============================================================

st.markdown(
    """
    <style>

    .main {
        background-color: #f8fafc;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    .hero {
        background: linear-gradient(
            135deg,
            #0f172a,
            #1e3a5f
        );
        padding: 2rem;
        border-radius: 18px;
        margin-bottom: 1.5rem;
        color: white;
    }

    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        margin-bottom: 0.3rem;
    }

    .hero-subtitle {
        font-size: 1.05rem;
        color: #dbeafe;
    }

    .section-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #0f172a;
        margin-top: 1.5rem;
        margin-bottom: 0.8rem;
    }

    .metric-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 1.2rem;
        text-align: center;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
    }

    .metric-label {
        font-size: 0.85rem;
        color: #64748b;
        margin-bottom: 0.3rem;
    }

    .metric-value {
        font-size: 1.7rem;
        font-weight: 800;
        color: #0f172a;
    }

    .metric-unit {
        font-size: 0.8rem;
        color: #64748b;
    }

    .prediction-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 3px 10px rgba(15, 23, 42, 0.05);
        margin-top: 1rem;
    }

    .prediction-label {
        font-size: 0.85rem;
        color: #64748b;
        margin-bottom: 0.3rem;
    }

    .prediction-value {
        font-size: 2rem;
        font-weight: 800;
        color: #0f172a;
    }

    .warning-card {
        background: #fff7ed;
        border: 1px solid #fed7aa;
        border-left: 6px solid #f97316;
        border-radius: 14px;
        padding: 1.3rem;
        margin-top: 1rem;
    }

    .warning-title {
        font-size: 1.2rem;
        font-weight: 800;
        color: #c2410c;
        margin-bottom: 0.4rem;
    }

    .warning-text {
        font-size: 0.95rem;
        color: #7c2d12;
    }

    .safe-card {
        background: #f0fdf4;
        border: 1px solid #bbf7d0;
        border-left: 6px solid #22c55e;
        border-radius: 14px;
        padding: 1.3rem;
        margin-top: 1rem;
    }

    .safe-title {
        font-size: 1.2rem;
        font-weight: 800;
        color: #15803d;
        margin-bottom: 0.4rem;
    }

    .safe-text {
        font-size: 0.95rem;
        color: #166534;
    }

    .info-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 14px;
        text-align: center;
        margin-top: 8px;
    }

    .info-label {
        font-size: 12px;
        color: #64748b;
        margin-bottom: 6px;
    }

    .info-value {
        font-size: 17px;
        font-weight: 700;
        color: #0f172a;
    }

    .api-status {
        border-radius: 10px;
        padding: 0.7rem;
        margin-top: 0.8rem;
        font-size: 0.82rem;
    }

    .api-online {
        background: #f0fdf4;
        border: 1px solid #bbf7d0;
        color: #166534;
    }

    .api-offline {
        background: #fef2f2;
        border: 1px solid #fecaca;
        color: #991b1b;
    }

    .footer {
        text-align: center;
        color: #64748b;
        font-size: 0.8rem;
        margin-top: 3rem;
        padding-top: 1rem;
        border-top: 1px solid #e2e8f0;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# Helper Functions
# ============================================================

def metric_card(label, value, unit=""):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-unit">{unit}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# Demo Data
# ============================================================

DEMO_DATA = pd.DataFrame(
    [
        {
            "datetime": "2013-03-01T00:00:00",
            "PM2_5": 30.0,
            "PM10": 45.0,
            "SO2": 12.0,
            "NO2": 40.0,
            "CO": 0.7,
            "O3": 60.0,
            "TEMP": 4.0,
            "PRES": 1020.0,
            "DEWP": -5.0,
            "RAIN": 0.0,
            "wd": "NW",
            "WSPM": 1.2,
            "station": "Aotizhongxin",
        },
        {
            "datetime": "2013-03-01T01:00:00",
            "PM2_5": 32.0,
            "PM10": 48.0,
            "SO2": 13.0,
            "NO2": 42.0,
            "CO": 0.8,
            "O3": 58.0,
            "TEMP": 3.0,
            "PRES": 1020.0,
            "DEWP": -5.0,
            "RAIN": 0.0,
            "wd": "NW",
            "WSPM": 1.1,
            "station": "Aotizhongxin",
        },
        {
            "datetime": "2013-03-01T02:00:00",
            "PM2_5": 35.0,
            "PM10": 52.0,
            "SO2": 14.0,
            "NO2": 45.0,
            "CO": 0.8,
            "O3": 55.0,
            "TEMP": 2.0,
            "PRES": 1019.0,
            "DEWP": -4.0,
            "RAIN": 0.0,
            "wd": "NW",
            "WSPM": 1.0,
            "station": "Aotizhongxin",
        },
        {
            "datetime": "2013-03-01T03:00:00",
            "PM2_5": 38.0,
            "PM10": 56.0,
            "SO2": 15.0,
            "NO2": 48.0,
            "CO": 0.9,
            "O3": 52.0,
            "TEMP": 2.0,
            "PRES": 1019.0,
            "DEWP": -4.0,
            "RAIN": 0.0,
            "wd": "NW",
            "WSPM": 0.9,
            "station": "Aotizhongxin",
        },
        {
            "datetime": "2013-03-01T04:00:00",
            "PM2_5": 40.0,
            "PM10": 60.0,
            "SO2": 16.0,
            "NO2": 50.0,
            "CO": 0.9,
            "O3": 50.0,
            "TEMP": 1.0,
            "PRES": 1018.0,
            "DEWP": -3.0,
            "RAIN": 0.0,
            "wd": "NW",
            "WSPM": 0.9,
            "station": "Aotizhongxin",
        },
        {
            "datetime": "2013-03-01T05:00:00",
            "PM2_5": 43.0,
            "PM10": 65.0,
            "SO2": 17.0,
            "NO2": 52.0,
            "CO": 1.0,
            "O3": 48.0,
            "TEMP": 1.0,
            "PRES": 1018.0,
            "DEWP": -3.0,
            "RAIN": 0.0,
            "wd": "NW",
            "WSPM": 0.9,
            "station": "Aotizhongxin",
        },
        {
            "datetime": "2013-03-01T06:00:00",
            "PM2_5": 45.0,
            "PM10": 70.0,
            "SO2": 18.0,
            "NO2": 55.0,
            "CO": 1.0,
            "O3": 45.0,
            "TEMP": 8.0,
            "PRES": 1018.0,
            "DEWP": -2.0,
            "RAIN": 0.0,
            "wd": "NW",
            "WSPM": 0.9,
            "station": "Aotizhongxin",
        },
    ]
)


# ============================================================
# Sidebar
# ============================================================

with st.sidebar:

    st.markdown(
        "## 🌬️ AirShift"
    )

    st.markdown(
        "### Controls"
    )

    selected_station = st.selectbox(
        "Monitoring Station",
        STATIONS,
    )

    use_demo = st.checkbox(
        "Use demo data",
        value=True,
    )

    st.caption(
        "Prediction requires at least 7 consecutive hourly observations."
    )

    # --------------------------------------------------------
    # API Health Check
    # --------------------------------------------------------

    try:

        health_response = requests.get(
            f"{API_URL}/health",
            timeout=2,
        )

        if health_response.status_code == 200:

            st.markdown(
                f"""
                <div class="api-status api-online">
                    🟢 Local API Online<br>
                    {API_URL}
                </div>
                """,
                unsafe_allow_html=True,
            )

        else:

            st.markdown(
                f"""
                <div class="api-status api-offline">
                    🔴 Local API Error<br>
                    {API_URL}
                </div>
                """,
                unsafe_allow_html=True,
            )

    except requests.exceptions.RequestException:

        st.markdown(
            f"""
            <div class="api-status api-offline">
                🔴 Local API Offline<br>
                {API_URL}
            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# Hero Header
# ============================================================

st.markdown(
    '<div class="hero">'
    '<div class="hero-title">🌬️ AirShift</div>'
    '<div class="hero-subtitle">'
    'Early Warning System for Air Quality Deterioration'
    '</div>'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    AirShift analyzes recent air quality and meteorological
    conditions to estimate the probability of
    <b>PM2.5 deterioration within the following six hours.</b>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# Data Input
# ============================================================

st.markdown(
    '<div class="section-title">Recent Air Quality Observations</div>',
    unsafe_allow_html=True,
)

if use_demo:

    data = DEMO_DATA.copy()

    data["station"] = selected_station

    st.info(
        "Demo data is loaded. Use it to test the prediction system."
    )

else:

    uploaded_file = st.file_uploader(
        "Upload recent air quality observations",
        type=["csv"],
    )

    if uploaded_file is None:

        st.warning(
            "Upload a CSV file containing at least "
            "7 consecutive hourly observations."
        )

        st.stop()

    try:

        data = pd.read_csv(
            uploaded_file
        )

    except Exception as e:

        st.error(
            f"Could not read the CSV file: {e}"
        )

        st.stop()

    required_columns = [
        "datetime",
        "PM2_5",
        "PM10",
        "SO2",
        "NO2",
        "CO",
        "O3",
        "TEMP",
        "PRES",
        "DEWP",
        "RAIN",
        "wd",
        "WSPM",
        "station",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in data.columns
    ]

    if missing_columns:

        st.error(
            "Missing required columns: "
            + ", ".join(missing_columns)
        )

        st.stop()

    data["datetime"] = pd.to_datetime(
        data["datetime"],
        errors="coerce",
    )

    if data["datetime"].isna().any():

        st.error(
            "The CSV contains invalid datetime values."
        )

        st.stop()

    if data["datetime"].duplicated().any():

        st.error(
            "Duplicate datetime values are not allowed."
        )

        st.stop()

    if data["station"].nunique() != 1:

        st.error(
            "All observations must belong to the same station."
        )

        st.stop()

    if len(data) < 7:

        st.error(
            "At least 7 hourly observations are required."
        )

        st.stop()

    data = (
        data
        .sort_values("datetime")
        .reset_index(drop=True)
    )

    time_difference = (
        data["datetime"]
        .diff()
        .dropna()
    )

    if not (
        time_difference == pd.Timedelta(hours=1)
    ).all():

        st.error(
            "Observations must be consecutive hourly measurements."
        )

        st.stop()

    if data["station"].iloc[0] not in STATIONS:

        st.error(
            f"Unknown monitoring station: "
            f"{data['station'].iloc[0]}"
        )

        st.stop()

    st.success(
        f"CSV validation passed — "
        f"{len(data)} observations ready for analysis."
    )


# ============================================================
# Current Conditions
# ============================================================

st.markdown(
    '<div class="section-title">Current Conditions</div>',
    unsafe_allow_html=True,
)

latest = data.iloc[-1]

condition_col1, condition_col2, condition_col3, condition_col4 = (
    st.columns(4)
)

with condition_col1:

    metric_card(
        "PM2.5",
        f"{latest['PM2_5']:.1f}",
        "μg/m³",
    )

with condition_col2:

    metric_card(
        "PM10",
        f"{latest['PM10']:.1f}",
        "μg/m³",
    )

with condition_col3:

    metric_card(
        "Temperature",
        f"{latest['TEMP']:.1f}",
        "°C",
    )

with condition_col4:

    metric_card(
        "Wind Speed",
        f"{latest['WSPM']:.1f}",
        "m/s",
    )


# ============================================================
# PM2.5 Trend
# ============================================================

st.markdown(
    '<div class="section-title">PM2.5 Trend</div>',
    unsafe_allow_html=True,
)

chart_data = data[
    ["datetime", "PM2_5"]
].copy()

chart_data = chart_data.rename(
    columns={
        "PM2_5": "PM2.5"
    }
)

chart_data["datetime"] = pd.to_datetime(
    chart_data["datetime"]
)

fig = px.line(
    chart_data,
    x="datetime",
    y="PM2.5",
    markers=True,
)

fig.update_layout(
    height=320,
    margin=dict(
        l=0,
        r=0,
        t=10,
        b=0,
    ),
    xaxis_title=None,
    yaxis_title="PM2.5 (μg/m³)",
    hovermode="x unified",
)

fig.update_traces(
    line=dict(width=3),
    marker=dict(size=7),
)

st.plotly_chart(
    fig,
    use_container_width=True,
)


# ============================================================
# Observation Table
# ============================================================

with st.expander(
    "View recent observations"
):

    st.dataframe(
        data,
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# Prediction Section
# ============================================================

st.markdown(
    '<div class="section-title">Early Warning Analysis</div>',
    unsafe_allow_html=True,
)

analyze = st.button(
    "🔍 Analyze Air Quality",
    use_container_width=True,
)


if analyze:

    # --------------------------------------------------------
    # Prepare API payload
    # --------------------------------------------------------

    payload_data = data.copy()

    payload_data["datetime"] = (
        pd.to_datetime(
            payload_data["datetime"]
        )
        .dt.strftime(
            "%Y-%m-%dT%H:%M:%S"
        )
    )

    payload = {
        "observations": payload_data.to_dict(
            orient="records"
        )
    }

    # --------------------------------------------------------
    # API Request
    # --------------------------------------------------------

    try:

        with st.spinner(
            "Analyzing air quality..."
        ):

            response = requests.post(
                f"{API_URL}/predict",
                json=payload,
                timeout=30,
            )

    except requests.exceptions.ConnectionError:

        st.error(
            "Could not connect to the AirShift API. "
            "Make sure FastAPI is running."
        )

        st.stop()

    except requests.exceptions.RequestException as e:

        st.error(
            f"API request failed: {e}"
        )

        st.stop()

    # --------------------------------------------------------
    # API Error
    # --------------------------------------------------------

    if response.status_code != 200:

        try:

            error_detail = response.json()

        except Exception:

            error_detail = response.text

        st.error(
            f"Prediction failed: {error_detail}"
        )

        st.stop()

    # --------------------------------------------------------
    # Prediction Result
    # --------------------------------------------------------

    result = response.json()

    probability = result[
        "deterioration_probability"
    ]

    threshold = result[
        "warning_threshold"
    ]

    early_warning = result[
        "early_warning"
    ]

    st.markdown(
        '<div class="prediction-card">',
        unsafe_allow_html=True,
    )

    st.markdown(
        "### Prediction Result"
    )

    result_col1, result_col2, result_col3 = (
        st.columns(3)
    )

    with result_col1:

        st.markdown(
            '<div class="prediction-label">'
            'Deterioration Probability'
            '</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            f'<div class="prediction-value">'
            f'{probability * 100:.1f}%'
            f'</div>',
            unsafe_allow_html=True,
        )

        st.caption(
            "Model prediction"
        )

    with result_col2:

        st.markdown(
            '<div class="prediction-label">'
            'Warning Threshold'
            '</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            f'<div class="prediction-value">'
            f'{threshold * 100:.0f}%'
            f'</div>',
            unsafe_allow_html=True,
        )

        st.caption(
            "Configured threshold"
        )

    with result_col3:

        st.markdown(
            '<div class="prediction-label">'
            'Monitoring Station'
            '</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            f'<div class="prediction-value">'
            f'{result["station"]}'
            f'</div>',
            unsafe_allow_html=True,
        )

        st.caption(
            "Prediction location"
        )

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # Probability Progress Bar
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">'
        'Deterioration Probability'
        '</div>',
        unsafe_allow_html=True,
    )

    st.progress(
        probability,
        text=(
            f"{probability * 100:.1f}% "
            "predicted probability"
        ),
    )

    if probability >= threshold:

        st.caption(
            f"Above the {threshold * 100:.0f}% "
            "warning threshold."
        )

    else:

        st.caption(
            f"Below the {threshold * 100:.0f}% "
            "warning threshold."
        )

    # --------------------------------------------------------
    # Warning Status
    # --------------------------------------------------------

    if early_warning:

        st.markdown(
            '<div class="warning-card">'
            '<div class="warning-title">'
            '⚠️ EARLY WARNING'
            '</div>'
            '<div class="warning-text">'
            'The model estimates an elevated probability '
            'of air quality deterioration within the '
            'following six hours.'
            '</div>'
            '</div>',
            unsafe_allow_html=True,
        )

    else:

        st.markdown(
            '<div class="safe-card">'
            '<div class="safe-title">'
            '🟢 NO EARLY WARNING'
            '</div>'
            '<div class="safe-text">'
            'The predicted probability is below the '
            'configured warning threshold.'
            '</div>'
            '</div>',
            unsafe_allow_html=True,
        )

    # --------------------------------------------------------
    # Prediction Time
    # --------------------------------------------------------

    st.caption(
        f"Prediction time: "
        f"{result['prediction_time']}"
    )

    # --------------------------------------------------------
    # Model Information
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">'
        'Model Information'
        '</div>',
        unsafe_allow_html=True,
    )

    info_col1, info_col2, info_col3, info_col4 = (
        st.columns(4)
    )

    with info_col1:

        st.markdown(
            '<div class="info-card">'
            '<div class="info-label">'
            'Model'
            '</div>'
            '<div class="info-value">'
            'XGBoost'
            '</div>'
            '</div>',
            unsafe_allow_html=True,
        )

    with info_col2:

        st.markdown(
            '<div class="info-card">'
            '<div class="info-label">'
            'Threshold'
            '</div>'
            '<div class="info-value">'
            '30%'
            '</div>'
            '</div>',
            unsafe_allow_html=True,
        )

    with info_col3:

        st.markdown(
            '<div class="info-card">'
            '<div class="info-label">'
            'Forecast Horizon'
            '</div>'
            '<div class="info-value">'
            '6 hours'
            '</div>'
            '</div>',
            unsafe_allow_html=True,
        )

    with info_col4:

        st.markdown(
            '<div class="info-card">'
            '<div class="info-label">'
            'Input Window'
            '</div>'
            '<div class="info-value">'
            '7 hours'
            '</div>'
            '</div>',
            unsafe_allow_html=True,
        )


# ============================================================
# Footer
# ============================================================

st.markdown(
    """
    <div class="footer">
        AirShift — Early Warning System for Air Quality Deterioration
    </div>
    """,
    unsafe_allow_html=True,
)
