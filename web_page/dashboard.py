import streamlit as st
import sqlite3
import pandas as pd
import time
import matplotlib.pyplot as plt

# Set page configuration
st.set_page_config(page_title="Predator Detection Dashboard", layout="wide")

# Apply Custom Styling
st.markdown("""
    <style>
        .title { 
            color: #FFFFFF; 
            font-size: 40px !important;  /* Increased font size */
            font-weight: bold; 
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown('<p class="title">🐔 Chicken Predator Detection Dashboard</p>', unsafe_allow_html=True)

# Connect to SQLite and fetch detection data
def fetch_data():
    conn = sqlite3.connect("../predator_data.db")
    df = pd.read_sql_query("SELECT * FROM detections", conn)
    conn.close()
    return df

# Sidebar Filters
st.sidebar.subheader("🔍 Filter Detections")
selected_date = st.sidebar.date_input("Select Date", pd.to_datetime("today"))

# Layout: Three Columns
col1, col2 = st.columns(2)

# Show Detection Logs
with col1:
    st.subheader("📋 Detection Logs")
    df = fetch_data()
    
    if not df.empty:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        filtered_df = df[df["timestamp"].dt.date == selected_date]
        st.write(filtered_df)
    else:
        st.write("No detections found.")

with col2:
    # Generate a Graph for Detections Per Hour
    st.subheader("📊 Predator Detection Trends")

    if not filtered_df.empty:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df["hour"] = df["timestamp"].dt.hour
        detections_per_hour = df.groupby("hour").size()

        # Plot the data
        fig, ax = plt.subplots()
        detections_per_hour.plot(kind="bar", color="#FF4B4B", ax=ax)
        ax.set_xlabel("Hour of the Day")
        ax.set_ylabel("Number of Detections")
        ax.set_title("Predator Detections Per Hour")
        st.pyplot(fig)
    else:
        st.write("No data available for trend analysis.")

