
import os
import streamlit as st
import pandas as pd
import plotly.express as px

from sqlalchemy import create_engine, text, URL
from dotenv import load_dotenv
from streamlit_autorefresh import st_autorefresh

# ---------------- CONFIGURATION ----------------

st.set_page_config(
    page_title="DistaSense AI",
    page_icon="📡",
    layout="wide"
)

load_dotenv()

# ---------------- CUSTOM CSS ----------------

st.markdown("""
<style>
.stApp {
    background-color: #0E1117;
    color: #FFFFFF;
}
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}
[data-testid="stMetric"] {
    background-color: #1B2230;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #303B4B;
}
[data-testid="stMetricLabel"] {
    color: #AAB4C3;
}
[data-testid="stMetricValue"] {
    color: #55D6BE;
}
h1, h2, h3 {
    color: #FFFFFF;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------

st.title("📡 DistaSense AI")
st.caption("Smart Ultrasonic Distance Monitoring System")

st_autorefresh(interval=5000, key="refresh")

# ---------------- DATABASE ----------------

@st.cache_resource
def get_engine():
    password = os.getenv("DB_PASSWORD")

    if not password:
        raise ValueError("DB_PASSWORD is missing from .env")

    db_url = URL.create(
        drivername="postgresql+psycopg",
        username=os.getenv("DB_USER", "postgres"),
        password=password,
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        database=os.getenv("DB_NAME", "distasense")
    )

    return create_engine(db_url, pool_pre_ping=True)


@st.cache_data(ttl=5)
def get_data():
    query = """
        SELECT id, timestamp, distance_cm, distance_change_cm
        FROM sensor_readings
        ORDER BY timestamp DESC
    """

    with get_engine().connect() as conn:
        df = pd.read_sql(text(query), conn)

    if not df.empty:
        df["timestamp"] = pd.to_datetime(df["timestamp"])

    return df


# ---------------- DASHBOARD ----------------

try:
    df = get_data()

    if df.empty:
        st.warning("No sensor readings available. Start your sensor data collection.")
        st.stop()

    latest = df.iloc[0]

    # Sensor freshness indicator
    current_time = pd.Timestamp.now()
    latest_time = latest["timestamp"]

    if latest_time.tzinfo is not None:
        current_time = current_time.tz_localize(latest_time.tzinfo)

    age = (current_time - latest_time).total_seconds()

    if age <= 15:
        st.success("🟢 Sensor data is updating")
    else:
        st.warning("🟠 No recent sensor readings")

    # ---------------- METRICS ----------------

    st.subheader("Live Overview")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Current Distance",
        f"{latest['distance_cm']:.2f} cm",
        f"{latest['distance_change_cm']:.2f} cm"
    )

    c2.metric(
        "Average Distance",
        f"{df['distance_cm'].mean():.2f} cm"
    )

    c3.metric(
        "Minimum Distance",
        f"{df['distance_cm'].min():.2f} cm"
    )

    c4.metric(
        "Total Readings",
        f"{len(df):,}"
    )

    st.divider()

    # ---------------- GRAPH ----------------

    left, right = st.columns([2, 1])

    with left:
        st.subheader("📈 Distance Monitoring")

        graph_df = df.sort_values("timestamp").tail(100)

        fig = px.line(
            graph_df,
            x="timestamp",
            y="distance_cm",
            markers=True,
            template="plotly_dark",
            labels={
                "timestamp": "Time",
                "distance_cm": "Distance (cm)"
            }
        )

        fig.update_traces(
            line=dict(width=3),
            marker=dict(size=5)
        )

        fig.update_layout(
            height=370,
            margin=dict(l=10, r=10, t=20, b=10),
            paper_bgcolor="#0E1117",
            plot_bgcolor="#151B25"
        )

        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.subheader("📊 Distance Summary")

        st.metric("Maximum", f"{df['distance_cm'].max():.2f} cm")
        st.metric("Minimum", f"{df['distance_cm'].min():.2f} cm")
        st.metric("Latest Change", f"{latest['distance_change_cm']:.2f} cm")

        st.caption(
            "Last reading: " +
            latest_time.strftime("%d-%m-%Y %H:%M:%S")
        )

    st.divider()

    # ---------------- RECENT READINGS ----------------

    st.subheader("📋 Recent Sensor Readings")

    recent = df.head(10).copy()

    recent["timestamp"] = recent["timestamp"].dt.strftime(
        "%d-%m-%Y %H:%M:%S"
    )

    recent.columns = [
        "ID",
        "Timestamp",
        "Distance (cm)",
        "Distance Change (cm)"
    ]

    st.dataframe(
        recent,
        use_container_width=True,
        hide_index=True
    )

    # ---------------- DOWNLOAD ----------------

    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "⬇️ Download Readings CSV",
        data=csv,
        file_name="distasense_readings.csv",
        mime="text/csv"
    )

    st.caption("DistaSense AI | Auto-refresh every 5 seconds")

except Exception as e:
    st.error(f"Database connection error: {e}")
    st.info("Check your PostgreSQL service, .env credentials and table columns.")

