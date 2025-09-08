import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Folder where attendance CSVs are saved
ATTENDANCE_DIR = "Attendance"

# Convert time string (HH:MM:SS) → seconds
def time_to_seconds(t):
    try:
        h, m, s = map(int, t.split(":"))
        return h*3600 + m*60 + s
    except:
        return 0

# Convert seconds → HH:MM:SS
def seconds_to_hms(seconds):
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h:02}:{m:02}:{s:02}"

# Page layout
st.set_page_config(page_title="Employee Attendance Dashboard", layout="wide")

st.title("📊 Employee Attendance Dashboard")

# Get all attendance files
files = sorted([f for f in os.listdir(ATTENDANCE_DIR) if f.endswith(".csv")])
if not files:
    st.warning("⚠️ No attendance records found yet.")
    st.stop()

# Extract available dates from filenames
available_dates = [datetime.strptime(f.replace("Attendance_", "").replace(".csv", ""), "%d-%m-%Y") for f in files]

# Date range picker
st.subheader("📅 Select Date Range")
date_range = st.date_input("Choose start and end date", value=[min(available_dates), max(available_dates)])

if len(date_range) != 2:
    st.warning("⚠️ Please select both start and end date.")
    st.stop()

start_date, end_date = date_range

# Filter files in selected date range
# Filter files in selected date range
selected_files = [
    f for f in files
    if start_date <= datetime.strptime(f.replace("Attendance_", "").replace(".csv", ""), "%d-%m-%Y").date() <= end_date
]


if not selected_files:
    st.warning("⚠️ No attendance files found in this date range.")
    st.stop()

# Load and merge CSVs
all_data = []
for file in selected_files:
    file_path = os.path.join(ATTENDANCE_DIR, file)
    df = pd.read_csv(file_path)
    df["DATE"] = file.replace("Attendance_", "").replace(".csv", "")
    all_data.append(df)

df_all = pd.concat(all_data, ignore_index=True).fillna("")

# Show logs
st.subheader("🔹 Attendance Logs")
st.dataframe(df_all, use_container_width=True)

# Calculate total worked time per employee
summary = []
for (emp_id, name), group in df_all.groupby(["EMP_ID", "NAME"]):
    total_sec = sum(time_to_seconds(t) for t in group["TOTAL_TIME"] if t != "")
    summary.append([emp_id, name, seconds_to_hms(total_sec)])

summary_df = pd.DataFrame(summary, columns=["EMP_ID", "NAME", "TOTAL_HOURS_WORKED"])

st.subheader("⏱ Total Hours Worked (Summary for Selected Range)")
st.dataframe(summary_df, use_container_width=True)

# Optional: Filter by employee
emp_filter = st.selectbox("👤 Filter by Employee", ["All"] + summary_df["NAME"].tolist())
if emp_filter != "All":
    emp_logs = df_all[df_all["NAME"] == emp_filter]
    st.subheader(f"📌 Detailed Logs for {emp_filter}")
    st.dataframe(emp_logs, use_container_width=True)
