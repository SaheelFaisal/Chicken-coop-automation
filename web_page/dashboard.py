import streamlit as st
import sqlite3
import pandas as pd
import time
import matplotlib.pyplot as plt

# Title
st.header("Chicken Predator Detection Dashboard", divider="grey")

# Connect to SQLite and fetch detection data
def fetch_detection_data():
    conn = sqlite3.connect("../predator_data.db")
    df = pd.read_sql_query("SELECT * FROM detections", conn)
    conn.close()
    return df

def fetch_chicken_count_data():
    conn = sqlite3.connect("../predator_data.db")
    df = pd.read_sql_query("SELECT * FROM chicken_count", conn)
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
    df = fetch_detection_data()
    
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

# Section for Chicken Count Data
st.subheader("🐔 Chicken Count Over Time")
chicken_df = fetch_chicken_count_data()

if not chicken_df.empty:
    chicken_df["Time"] = pd.to_datetime(chicken_df["Time"])
    st.write(chicken_df)

    # Plot Chicken Count Over Time
    fig2, ax2 = plt.subplots()
    ax2.plot(chicken_df["Time"], chicken_df["Count"], marker='o', linestyle='-', color="#FFA500")
    ax2.set_xlabel("Time")
    ax2.set_ylabel("Chicken Count")
    ax2.set_title("Chicken Count Over Time")
    st.pyplot(fig2)
else:
    st.write("No chicken count data available.")
