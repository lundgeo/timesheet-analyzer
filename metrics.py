import pandas as pd

def weekly_hours_by_project(data: pd.DataFrame) -> pd.DataFrame:
    return data.groupby(['week_ending','project_name'])['total'].sum().reset_index()

def prior_two_months_hours_by_project(data: pd.DataFrame) -> pd.DataFrame:
    most_recent_week = data['week_ending'].max()
    last_two_months = data[data['week_ending'] > most_recent_week - pd.DateOffset(months=2)]
    return last_two_months.groupby('project_name')['total'].sum().reset_index()

def primary_project_last_week(data: pd.DataFrame) -> str:
    most_recent_week = data['week_ending'].max()
    last_week = data[data['week_ending']==most_recent_week].groupby(['week_ending','project_name'])['total'].sum().reset_index()
    max_project_hours = last_week.groupby('project_name')['total'].sum().max()
    primary_project_last_week = last_week[last_week['total'] == max_project_hours]['project_name'].values[0]
    return primary_project_last_week

def percentage_of_time_on_most_recent_project(data: pd.DataFrame) -> (str, str):
    main_project = primary_project_last_week(data)
    last_two_months = prior_two_months_hours_by_project(data)
    time_on_most_recent_project = last_two_months[last_two_months['project_name'] == main_project]
    return main_project, f'{((time_on_most_recent_project['total'] / last_two_months['total'].sum()).max() * 100).round(1)}%'


def has_been_on_current_project_for_a_while(data: pd.DataFrame) -> pd.DataFrame:
    last_two_months = prior_two_months_hours_by_project(data)

    last_two_months['percentage'] = last_two_months['total'] / last_two_months['total'].sum() * 100
    last_two_months['percentage'] = last_two_months['percentage'].round(1)
    last_two_months['dollars'] = last_two_months['total'] * 185
    last_two_months['dollars'] = last_two_months['dollars'].round(2)
    
    print(*percentage_of_time_on_most_recent_project(data))
    return last_two_months