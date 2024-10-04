import pandas as pd


def weekly_hours_by_project(data: pd.DataFrame, months: int = None) -> pd.DataFrame:
    if months:
        data = data[
            data["week_ending"]
            > data["week_ending"].max() - pd.DateOffset(months=months)
        ]
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

    return prior_months


def _calculate_rotation_index(row, all_data, weeks_to_include=3, recent_weeks=8):
    project_total_for_week_of_row = (
        all_data[
            (
                all_data["week_ending"]
                > row["week_ending"] - pd.DateOffset(weeks=weeks_to_include)
            )
            & (all_data["week_ending"] <= row["week_ending"])
        ]
        .groupby("project_name")["total_time_billed"]
        .sum()
        .reset_index()
    )
    project_with_most_hours_during_week_of_row = (
        project_total_for_week_of_row.groupby("project_name")["total_time_billed"]
        .sum()
        .max()
    )
    main_project_for_current_week = project_total_for_week_of_row[
        project_total_for_week_of_row["total_time_billed"]
        == project_with_most_hours_during_week_of_row
    ]["project_name"].values[0]

    last_n_months = all_data[
        (
            all_data["week_ending"]
            > row["week_ending"] - pd.DateOffset(weeks=recent_weeks)
        )
        & (all_data["week_ending"] <= row["week_ending"])
    ]
    total_last_n_months = last_n_months["total_time_billed"].sum()
    last_n_months_on_current_project = last_n_months[
        last_n_months["project_name"] == main_project_for_current_week
    ]["total_time_billed"].sum()
    rotation_index = 1 - last_n_months_on_current_project / total_last_n_months

    return pd.Series(
        [main_project_for_current_week, rotation_index],
        index=["main_project", "rotation_index"],
    )


def caluculate_rotation_index(
    data: pd.DataFrame, weeks_to_include=3, recent_weeks=8
) -> pd.DataFrame:
    weekly_hours_by_project = (
        data.groupby(["week_ending", "project_name"])["total_time_billed"]
        .sum()
        .reset_index()
    )
    rotation_index = pd.DataFrame()
    rotation_index["week_ending"] = data["week_ending"].unique()

    rotation_index[["main_project", "rotation_index"]] = rotation_index.apply(
        lambda row: _calculate_rotation_index(
            row, weekly_hours_by_project, weeks_to_include, recent_weeks=recent_weeks
        ),
        axis=1,
    )
    return rotation_index


def sum_of_hours_per_storycard(data: pd.DataFrame) -> pd.DataFrame:
    return_data = (
        data.groupby(["project_name", "storycard_number"])["total_time_billed"]
        .sum()
        .reset_index()
    )
    output = pd.DataFrame()
    output["text"] = return_data.apply(
        lambda row: f"The time in hours spent working on the storycard {row['storycard_number']} on the {row['project_name']} project was the following total: {row['total_time_billed']}",
        axis=1,
    )
    output.to_csv("storycard_totals.csv", index=False)
    return return_data
