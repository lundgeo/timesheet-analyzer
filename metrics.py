import pandas as pd


def weekly_hours_by_project(data: pd.DataFrame, months:int = None) -> pd.DataFrame:
    if months:
        data = data[data["week_ending"] > data["week_ending"].max() - pd.DateOffset(months=months)]
    weekly_project_totals = (
        data.groupby(["week_ending", "project_name"])["total_time_billed"]
        .sum()
        .reset_index()
    )

    weekly_totals = data.groupby("week_ending")["total_time_billed"].sum().reset_index()
    weekly_totals = weekly_totals.rename(
        columns={"total_time_billed": "weekly_total_time_billed"}
    )

    merged_data = pd.merge(weekly_project_totals, weekly_totals, on="week_ending")

    merged_data["percentage"] = (
        merged_data["total_time_billed"] / merged_data["weekly_total_time_billed"]
    ) * 100
    return merged_data


def total_hours_by_project(data: pd.DataFrame) -> pd.DataFrame:
    return data.groupby("project_name")["total_time_billed"].sum().reset_index()


def prior_months_hours_by_project(data: pd.DataFrame, months=2) -> pd.DataFrame:
    most_recent_week = data["week_ending"].max()
    last_n_months = data[
        data["week_ending"] > most_recent_week - pd.DateOffset(months=months)
    ]
    return (
        last_n_months.groupby("project_name")["total_time_billed"].sum().reset_index()
    )


def primary_project_last_week(data: pd.DataFrame) -> str:
    most_recent_week = data["week_ending"].max()
    last_week = (
        data[data["week_ending"] == most_recent_week]
        .groupby(["week_ending", "project_name"])["total_time_billed"]
        .sum()
        .reset_index()
    )
    max_project_hours = (
        last_week.groupby("project_name")["total_time_billed"].sum().max()
    )
    main_project_last_week = last_week[
        last_week["total_time_billed"] == max_project_hours
    ]["project_name"].values[0]
    return main_project_last_week


def percentage_of_time_on_most_recent_project(data: pd.DataFrame) -> tuple[str, str]:
    main_project = primary_project_last_week(data)
    last_two_months = prior_months_hours_by_project(data)
    time_on_most_recent_project = last_two_months[
        last_two_months["project_name"] == main_project
    ]
    recent_project_percentage = (
        time_on_most_recent_project["total_time_billed"]
        / last_two_months["total_time_billed"].sum()
    )
    return main_project, f"{(recent_project_percentage.max() * 100).round(1)}%"


def additional_metrics_on_prior_months(data: pd.DataFrame, months=2) -> pd.DataFrame:
    prior_months = prior_months_hours_by_project(data, months)

    prior_months["percentage"] = (
        prior_months["total_time_billed"]
        / prior_months["total_time_billed"].sum()
        * 100
    ).round(1)
    prior_months["dollars"] = (prior_months["total_time_billed"] * 185).round(2)

    print(*percentage_of_time_on_most_recent_project(data))
    return prior_months
