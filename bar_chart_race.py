import random
import sys
from matplotlib import cm
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pandas as pd
import numpy as np
import seaborn as sns
import functools
from parse_timesheet import parse_files

def plot(data: pd.DataFrame):
    data['project_name'] = data['project_name'].str.upper()
    data["week_ending"] = pd.to_datetime(data["week_ending"])
    data["storycard_number"] = data["storycard_number"].astype(str)
    data["total_time_billed"] = pd.to_numeric(data["total_time_billed"], errors='coerce').fillna(0)

    grouped_data = data.groupby(["week_ending", "project_name"]).sum().reset_index()
    pivot_data = grouped_data.pivot(index="week_ending", columns="project_name", values="total_time_billed").fillna(0)

    unique_projects = pivot_data.columns  
    colors = sns.color_palette('hls', len(unique_projects))
    project_color_map = {project: colors[i] for i, project in enumerate(unique_projects)}  

    draw_barchart_partial = functools.partial(draw_barchart, pivot_data=pivot_data, project_color_map=project_color_map)

    fig, ax = plt.subplots(figsize=(10, 6))
    animator = animation.FuncAnimation(fig, draw_barchart_partial, frames=len(pivot_data), repeat=False)

    fig_manager = plt.get_current_fig_manager()
    fig_manager.full_screen_toggle()

    plt.show()

def draw_barchart(week, pivot_data: pd.DataFrame, project_color_map: dict[str, tuple]):
    plt.clf()
    current_week_data = pivot_data.iloc[:week+1].sum(axis=0).sort_values(ascending=False)
    current_week_data = current_week_data.head(15)[::-1] 
    colors = [project_color_map[project] for project in current_week_data.index if project in project_color_map]

    bars = plt.barh(current_week_data.index, current_week_data.values, color=colors)
    plt.xlim(0, current_week_data.max() + 5)
    plt.xlabel("Hours")
    plt.title(f'Total Time Billed up to {pivot_data.index[week].date()}')

    for bar in bars:
        width = bar.get_width()  
        plt.text(width + 0.5, bar.get_y() + bar.get_height() / 2, 
                f'{int(width)}', 
                va='center', ha='left')  

def read_csv(file_name: str):
    try:
        return pd.read_csv(sys.argv[1])
    except Exception as e:
        print(f"Error reading csv {file_name}. Parsing files to 'cached_timesheets.csv'")
        data = parse_files()
        data.to_csv('cached_timesheets.csv', index=True)
        return data

if __name__ == "__main__":
    data = pd.DataFrame()
    if len(sys.argv) > 1:
        data = read_csv(sys.argv[1])
    else:
        data = parse_files()
        data.to_csv('cached_timesheets.csv', index=True)
    plot(data)