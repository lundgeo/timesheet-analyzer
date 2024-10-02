import math
from matplotlib import pyplot as plt
import streamlit as st
import pandas as pd
from pathlib import Path
import altair as alt


from metrics import has_been_on_current_project_for_a_while
from parse_timesheet import parse_files

@st.cache_data
def fetch_data():
    output_file = Path.cwd() / 'final_data.json'
    if not output_file.exists():
        return pd.read_json(output_file)
    else:
        return parse_files()

final_data = fetch_data()

# Set the title of the dashboard
st.title("Timesheet Data Dashboard")

st.subheader("Summary by Project")
project_summary = final_data.groupby('project_name')['total'].sum().reset_index()
st.dataframe(project_summary)

st.subheader("Interactive Chart of Total Hours by Role")
project_summary = project_summary.sort_values(by='total', ascending=False).head(10)
chart = alt.Chart(project_summary).mark_bar().encode(
    x=alt.X('project_name', sort='-y'),
    y='total',
    tooltip=['project_name', 'total'],
).interactive()

st.altair_chart(chart, use_container_width=True)
plt.plot(project_summary['project_name'], project_summary['total'])
st.pyplot(plt.gcf())

# Add a filter for project names
project_names = final_data['project_name'].unique()
selected_project = st.selectbox("Select a project", project_names)

# Filter the DataFrame based on the selected project
filtered_data = final_data[final_data['project_name'] == selected_project].groupby('storycard')['total'].sum().reset_index()

# Display the filtered DataFrame
st.subheader(f"Data for Project: {selected_project}")
st.dataframe(filtered_data)

chart_two = alt.Chart(filtered_data.where(filtered_data['total']>2)).mark_bar().encode(
    x=alt.X('storycard', sort='-y'),
    y='total',
    tooltip=['storycard', 'total'],
).interactive()
st.altair_chart(chart_two, use_container_width=True)

st.subheader("Pie Chart of Total Hours by Storycard")
top_n = math.floor(filtered_data.shape[0] * 0.2)
filtered_data = filtered_data.sort_values(by='total', ascending=False)
first_ten = filtered_data.head(top_n)
filtered_data['category'] = filtered_data.apply(
    lambda row: row['storycard'] if row['storycard'] in list(first_ten['storycard']) else 'Other', axis=1
)
grouped_data = filtered_data.groupby('category')['total'].sum().reset_index()
grouped_data = grouped_data.sort_values(by='total', ascending=False)



# Add a download button for the filtered data
st.subheader("Download Filtered Data")
st.download_button(
    label="Download as CSV",
    data=filtered_data.to_csv(index=False),
    file_name=f"{selected_project}_data.csv",
    mime="text/csv"
)

st.subheader("Last Two Months")
selection = alt.selection_point()

last_two_months = has_been_on_current_project_for_a_while(final_data)
st.dataframe(last_two_months)
pie_chart = alt.Chart(last_two_months).mark_arc().encode(
    theta=alt.Theta(field="percentage", type="quantitative"),
    color=alt.Color(field="project_name", type="nominal"),
    tooltip=['project_name', 'percentage'],
    opacity=alt.condition(selection, alt.value(1), alt.value(0.2))

).add_params(selection).interactive()
st.altair_chart(pie_chart, use_container_width=True)
most_recent_week = final_data['week_ending'].max()
filtered_data = final_data[final_data['week_ending'] > most_recent_week - pd.DateOffset(months=2)]
st.dataframe(filtered_data)