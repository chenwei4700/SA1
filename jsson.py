import gspread
from google.oauth2.service_account import Credentials

# 設定 Google Sheets API
SERVICE_ACCOUNT_FILE = "api.json"  # 你的 JSON 金鑰
SPREADSHEET_ID = "https://docs.google.com/spreadsheets/d/1C_qYknxD84tMd3yAFMmYepNHa2raJJXEbp8ZL01HeMc/edit?gid=0#gid=0"  # 你的試算表 ID

scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=scopes)
client = gspread.authorize(creds)

# 讀取試算表
sheet = client.open_by_key(SPREADSHEET_ID).sheet1
data = sheet.get_all_values()

# 轉換成 FAQ 字典
faq = {row[0]: row[1] for row in data if len(row) == 2}

# 印出 FAQ
print(faq)
