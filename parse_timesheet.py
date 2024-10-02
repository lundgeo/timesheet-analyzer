from pathlib import Path
import pandas as pd

timesheets_folder = Path.cwd() / 'input_files'

def parse_file(file_path: Path) -> pd.DataFrame:
  df = pd.read_excel(file_path)
  date = df.iloc[1,2]
  data = df[4:]
  if data.shape[1] == 12:
    data.columns = ['blank', 'company', 'project_code', 'role_and_storycard', 'sat', 'sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'total']
  elif data.shape[1] == 13:
    data.columns = ['blank', 'company', 'project_code', 'role_and_storycard', 'blank_two', 'sat', 'sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'total']
  elif data.shape[1] == 14:
    data.columns = ['blank', 'company', 'project_code', 'role_and_storycard', 'blank_two', 'sat', 'sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'total', 'notes']
  else:
    raise ValueError('Invalid columns')

  data = data[pd.notna(data['project_code']) & pd.notna(data['total']) & pd.notna(data['role_and_storycard'])]
  if data.shape[0] == 0:
    return pd.DataFrame()
  data['project_name'] = data.apply(
      lambda row: row['role_and_storycard'].split(" ")[0] if 'SOW' in row['project_code'] else row['project_code'],
      axis=1
  )
  data['role'] = data.apply(
      lambda row: row['role_and_storycard'].split(" ")[1] if 'SOW' in row['project_code'] else 'N/A',
      axis=1
  )
  data['storycard'] = data.apply(
      lambda row: row['role_and_storycard'].split(" - ")[-1] if 'SOW' in row['project_code'] else row['role_and_storycard'],
      axis=1
  )
  data['total'] = data['total'].astype(float)
  data['week_ending'] = date
  return data[['week_ending', 'role','project_name','storycard', 'total']]

def parse_files():
  all_data = []

  for file in timesheets_folder.iterdir():
      if file.suffix == '.xlsx' or file.suffix == '.xls':
          try:
              parsed_data = parse_file(file)
              if not parsed_data.empty:
                  all_data.append(parsed_data)
          except Exception as e:
              print(f'Error parsing {file.name}: {e}')

  # Concatenate all DataFrames in the list
  if all_data:
      final_data = pd.concat(all_data, ignore_index=True)
      output_file = Path.cwd() / 'final_data.json'
      final_data.to_json(output_file, orient='records')
      print(f"Final data written to {output_file}")
  else:
      print("No valid data found.")
  return final_data