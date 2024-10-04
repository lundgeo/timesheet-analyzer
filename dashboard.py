import math
from matplotlib import pyplot as plt
import streamlit as st
import pandas as pd
from pathlib import Path
import altair as alt


from metrics import additional_metrics_on_prior_months, weekly_hours_by_project
from parse_timesheet import parse_files


@st.cache_data
def fetch_data():
    return parse_files()


final_data = fetch_data()

st.title("Timesheet Data Dashboard")

st.subheader("Total Hours by Project")
project_summary = (
    final_data.groupby("project_name")["total_time_billed"].sum().reset_index()
)
st.dataframe(project_summary)
project_summary = project_summary.sort_values(
    by="total_time_billed", ascending=False
).head(10)
chart = (
    alt.Chart(project_summary)
    .mark_bar()
    .encode(
        x=alt.X("project_name", sort="-y"),
        y="total_time_billed",
        tooltip=["project_name", "total_time_billed"],
    )
    .interactive()
)
st.altair_chart(chart, use_container_width=True)

st.subheader("Storycard Hours by Project")
project_names = sorted(final_data["project_name"].unique())
selected_project = st.selectbox("Select a project", project_names)

filtered_data = (
    final_data[final_data["project_name"] == selected_project]
    .groupby("storycard_number")["total_time_billed"]
    .sum()
    .reset_index()
)

st.subheader(f"Data for Project: {selected_project}")
st.dataframe(filtered_data)

chart_two = (
    alt.Chart(filtered_data.where(filtered_data["total_time_billed"] > 2))
    .mark_bar()
    .encode(
        x=alt.X("storycard_number", sort="-y"),
        y="total_time_billed",
        tooltip=["storycard_number", "total_time_billed"],
    )
    .interactive()
)
st.altair_chart(chart_two, use_container_width=True)

top_n = math.floor(filtered_data.shape[0] * 0.2)
filtered_data = filtered_data.sort_values(by="total_time_billed", ascending=False)
first_ten = filtered_data.head(top_n)
filtered_data["category"] = filtered_data.apply(
    lambda row: (
        row["storycard_number"]
        if row["storycard_number"] in list(first_ten["storycard_number"])
        else "Other"
    ),
    axis=1,
)

st.download_button(
    label="Download data above as CSV",
    data=filtered_data.to_csv(index=False),
    file_name=f"{selected_project}_data.csv",
    mime="text/csv",
)

st.subheader("Last Two Months")

last_two_months = additional_metrics_on_prior_months(final_data)
st.dataframe(last_two_months)
pie_chart = (
    alt.Chart(last_two_months)
    .mark_arc()
    .encode(
        theta=alt.Theta(field="percentage", type="quantitative"),
        color=alt.Color(field="project_name", type="nominal"),
        tooltip=["project_name", "percentage"],
    )
)
st.altair_chart(pie_chart, use_container_width=True)
most_recent_week = final_data["week_ending"].max()
filtered_data = final_data[
    final_data["week_ending"] > most_recent_week - pd.DateOffset(months=2)
]
st.dataframe(filtered_data)

st.subheader("Time Breakdown by Project")
months = st.selectbox(
    "Select a number of previous months to include",
    [1, 2, 4, 6, 12, 24, 36, 48, 60, 100],
    5,
)
weekly_hours = weekly_hours_by_project(final_data, months=months)
project_breakdown_chart = (
    alt.Chart(weekly_hours)
    .mark_bar()
    .encode(
        x=alt.X("week_ending", sort="x"),
        y="percentage",
        color="project_name",
        tooltip=["week_ending", "percentage", "project_name"],
    )
).interactive()
st.altair_chart(project_breakdown_chart, use_container_width=True)
