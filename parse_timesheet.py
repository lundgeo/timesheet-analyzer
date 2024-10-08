from pathlib import Path
import pandas as pd

timesheets_folder = Path.cwd() / "input_files"


def parse_project_name(row) -> str:
    if "SOW" in row["project_code"]:
        return row["role_and_storycard_number"].split(" ")[0]
    else:
        return row["project_code"]


def parse_role(row) -> str:
    if "SOW" in row["project_code"]:
        return row["role_and_storycard_number"].split(" ")[1]
    else:
        return "N/A"


def parse_storycard_number(row) -> str:
    if "SOW" in row["project_code"]:
        if " – " in row["role_and_storycard_number"]:
            return row["role_and_storycard_number"].split(" – ")[-1]
        else:
            return row["role_and_storycard_number"].split(" - ")[-1]
    else:
        return row["role_and_storycard_number"]


def parse_file(file_path: Path) -> pd.DataFrame:
    df = pd.read_excel(file_path)
    date = df.iloc[1, 2]
    data = df[4:]
    if data.shape[1] == 12:
        data.columns = [
            "blank",
            "company",
            "project_code",
            "role_and_storycard_number",
            "sat",
            "sun",
            "mon",
            "tue",
            "wed",
            "thu",
            "fri",
            "total_time_billed",
        ]
    elif data.shape[1] == 13:
        data.columns = [
            "blank",
            "company",
            "project_code",
            "role_and_storycard_number",
            "blank_two",
            "sat",
            "sun",
            "mon",
            "tue",
            "wed",
            "thu",
            "fri",
            "total_time_billed",
        ]
    elif data.shape[1] == 14:
        data.columns = [
            "blank",
            "company",
            "project_code",
            "role_and_storycard_number",
            "blank_two",
            "sat",
            "sun",
            "mon",
            "tue",
            "wed",
            "thu",
            "fri",
            "total_time_billed",
            "notes",
        ]
    else:
        raise ValueError("Invalid columns")

    data = data[
        pd.notna(data["project_code"])
        & pd.notna(data["total_time_billed"])
        & pd.notna(data["role_and_storycard_number"])
    ]

    if data.shape[0] == 0:
        return pd.DataFrame()

    data["project_name"] = data.apply(parse_project_name, axis=1)
    data["role"] = data.apply(parse_role, axis=1)
    data["storycard_number"] = data.apply(parse_storycard_number, axis=1)
    data["total_time_billed"] = data["total_time_billed"].astype(float)
    data["week_ending"] = date
    return data[
        ["week_ending", "role", "project_name", "storycard_number", "total_time_billed"]
    ]


def parse_files():
    all_data = []
    if not timesheets_folder.exists():
        raise FileNotFoundError("Put timesheets in a folder called 'input_files'.")
    for file in timesheets_folder.iterdir():
        if file.suffix == ".xlsx" or file.suffix == ".xls":
            try:
                parsed_data = parse_file(file)
                if not parsed_data.empty:
                    all_data.append(parsed_data)
            except Exception as e:
                print(f"Error parsing {file.name}: {e}")

    if all_data:
        final_data = pd.concat(all_data, ignore_index=True)
        return final_data
    else:
        print("No valid data found.")
        return pd.DataFrame()


if __name__ == "__main__":
    parse_files()
