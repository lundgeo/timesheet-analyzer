# Menlo Timesheet Analyser
This is currently a humble set of scripts for parsing Menlo-formatted timesheets into Pandas DataFrames. Very little effort went into parsing correctly, so look at your results before drawing broad conclusions. 

Please make whatever changes you want to this code. Everything is experimental.

## Setup
1. Pull repository
2. Create virtual environment (or not, it's your computer)
3. Install dependencies `pip install -r requirements.txt`
4. Put your timesheets in a folder in the root directory called `input_files`

## To Run the Dashboard
To run the web dashboard, enter this in the terminal: `streamlit run dashboard.py`

## To Run the Timesheet Backup Utility
1. Install the following onto your machine or your virtual environment `pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib`
2. Run the command `py timesheet_gmail_backup.py`
3. Make a `.env` file and add a line as suggested in the Developers Zoom Chat.
4. If you are using the utility for the first time you will be asked to login to your work Gmail and authorize the app.
5. Once authorized, wait for the utility to finish running.
6. Once finished, any attachment you sent to the Timesheet email address will be saved to the input_file directory.
Note: If your files are not .xlsx they may not be parsed correctly.  Consider using the XLSX conversion utility below

## To Run the Timesheet Backup Utility
1. Install the following onto your machine or your virtual environment `pip install pyexcel-xlsx pyexcel-ods3`
2. Rum the command `py timesheet_convert_to_excel.py`
Note: This utility will create a copy of .ods files converted to .xlsx files AND DELETE THE ORIGINAL ODS COPY.