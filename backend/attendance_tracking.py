# import pandas as pd
# from google.oauth2.service_account import Credentials
# from googleapiclient.discovery import build
# import gspread
# import io
# from googleapiclient.http import MediaIoBaseDownload

# # ---------- Setup Authentication ----------
# SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
# SERVICE_ACCOUNT_FILE = 'credentials.json'

# print("started")

# creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
# drive_service = build('drive', 'v3', credentials=creds)

# # ---------- Find Folders Containing "SE Project" ----------
# def get_se_project_folders():
#     folders = []
#     page_token = None
#     while True:
#         response = drive_service.files().list(
#             q="mimeType='application/vnd.google-apps.folder' and name contains 'SE Project'",
#             spaces='drive',
#             fields='nextPageToken, files(id, name)',
#             pageToken=page_token
#         ).execute()

#         folders.extend(response.get('files', []))
#         page_token = response.get('nextPageToken', None)
#         if page_token is None:
#             break
#     return folders

# # ---------- Get All CSV Files in a Folder ----------
# def get_csv_files_from_folder(folder_id):
#     response = drive_service.files().list(
#         q=f"'{folder_id}' in parents and mimeType='application/vnd.google-apps.spreadsheet'",
#         spaces='drive',
#         fields='files(id, name)'
#     ).execute()
#     return response.get('files', [])

# # ---------- Download and Parse Spreadsheet ----------
# def read_spreadsheet(file_id):
#     gc = gspread.authorize(creds)
#     sheet = gc.open_by_key(file_id).sheet1
#     data = sheet.get_all_records()
#     return pd.DataFrame(data)

# # ---------- Main Logic ----------
# all_data = []
# folders = get_se_project_folders()

# print(f"Found {len(folders)} folders with 'SE Project'")

# for folder in folders:
#     csv_files = get_csv_files_from_folder(folder['id'])
#     print(f"Processing folder: {folder['name']} ({len(csv_files)} files)")

#     for file in csv_files:
#         try:
#             df = read_spreadsheet(file['id'])
#             df['Meeting'] = file['name']
#             all_data.append(df)
#         except Exception as e:
#             print(f"Failed to read {file['name']} - {e}")

# if not all_data:
#     print("No data found.")
#     exit()

# # ---------- Combine and Clean Data ----------
# attendance_data = pd.concat(all_data, ignore_index=True)

# # Normalize column names
# attendance_data.columns = [col.strip().lower().replace(' ', '_') for col in attendance_data.columns]

# # Assume columns: name, email, duration
# attendance_data['duration_min'] = attendance_data['duration'].astype(str).str.extract('(\d+)').astype(int)

# # ---------- Summary Calculations ----------
# meetings_attended = attendance_data.groupby('email')['meeting'].nunique().reset_index()
# meetings_attended.columns = ['email', 'meetings_attended']

# total_time_spent = attendance_data.groupby('email')['duration_min'].sum().reset_index()
# total_time_spent.columns = ['email', 'total_time_minutes']

# summary = pd.merge(meetings_attended, total_time_spent, on='email')
# summary = summary.sort_values(by='meetings_attended', ascending=False)

# # ---------- Export Summary ----------
# summary.to_csv("attendance_summary.csv", index=False)
# print("✅ Attendance summary saved to 'attendance_summary.csv'")
# print("ended")




import os
import pandas as pd

# Base local folder where attendance folders are stored
BASE_DIR = "assets/attendance"
TARGET_KEYWORD = "SE Project"
SUPPORTED_EXTENSIONS = (".csv", ".xlsx")
all_data = []

print("🔍 Scanning folders...")

# Traverse folders
for folder_name in os.listdir(BASE_DIR):
    folder_path = os.path.join(BASE_DIR, folder_name)
    if os.path.isdir(folder_path) and TARGET_KEYWORD.lower() in folder_name.lower():
        print(f"📁 Processing folder: {folder_path}")
        for file_name in os.listdir(folder_path):
            if file_name.lower().endswith(SUPPORTED_EXTENSIONS):
                file_path = os.path.join(folder_path, file_name)
                try:
                    df = pd.read_excel(file_path) if file_name.endswith(".xlsx") else pd.read_csv(file_path)
                    df['Meeting'] = file_name
                    all_data.append(df)
                except Exception as e:
                    print(f"❌ Failed to read {file_name}: {e}")

if not all_data:
    print("⚠️ No attendance data found.")
    exit()

# Combine all files
attendance_df = pd.concat(all_data, ignore_index=True)

# Normalize column names
attendance_df.columns = [col.strip().lower().replace(' ', '_') for col in attendance_df.columns]

# Fallback for 'email' column
if 'email' not in attendance_df.columns and 'e-mail_address' in attendance_df.columns:
    attendance_df.rename(columns={'e-mail_address': 'email'}, inplace=True)

# Drop entries with missing first name
attendance_df = attendance_df[attendance_df['first_name'].notna()]
attendance_df['first_name'] = attendance_df['first_name'].str.strip().str.title()  # normalize casing

# Duration parsing
def parse_duration(val):
    try:
        val = str(val).strip().lower()
        if 'min' in val:
            return int(val.replace('min', '').strip())
        elif 'm' in val:
            return int(val.replace('m', '').strip())
        elif val.isdigit():
            return int(val)
        else:
            return 0
    except:
        return 0

attendance_df['duration_minutes'] = attendance_df['duration'].apply(parse_duration) if 'duration' in attendance_df.columns else 0

# Group by first_name
meeting_counts = attendance_df.groupby('first_name')['meeting'].nunique().reset_index(name='meetings_attended')
total_duration = attendance_df.groupby('first_name')['duration_minutes'].sum().reset_index(name='total_time_minutes')

# Merge and sort
summary_df = pd.merge(meeting_counts, total_duration, on='first_name')
summary_df = summary_df.sort_values(by='meetings_attended', ascending=False)

# Save output
summary_df.to_csv("attendance_summary_by_name.csv", index=False)
print("✅ Summary written to 'attendance_summary_by_name.csv'")



