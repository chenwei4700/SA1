from flask import Flask, jsonify, request
import gspread
from google.oauth2.service_account import Credentials
from collections import defaultdict
from googleapiclient.discovery import build

app = Flask(__name__)

# Google Sheets API 設定
SERVICE_ACCOUNT_FILE = "api.json"  # 你的 JSON 金鑰
SPREADSHEET_ID = "1C_qYknxD84tMd3yAFMmYepNHa2raJJXEbp8ZL01HeMc"  # 你的試算表 ID

# 設定 Google Sheets API 權限
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=scopes)
client = gspread.authorize(creds)

@app.route("/faq", methods=["GET"])
def get_faq():
    """從 Google 試算表讀取 FAQ 並回傳 JSON"""
    sheet = client.open_by_key(SPREADSHEET_ID).sheet1
    data = sheet.get_all_values()

    # 🔹 DEBUG：先印出 data 看看
    print("試算表內容：", data)

    # ✅ 跳過第一行（標題行）
    faq = defaultdict(list)
    for row in data[1:]:  # 跳過第一行
        if len(row) >= 2:
            faq[row[0]].append(row[1])

    return jsonify({"faq": faq})

@app.route("/webhook", methods=["POST"])
def webhook():
    """從 Dialogflow 接收請求並回傳 FAQ 答案"""
    req = request.get_json()
    question = req.get("queryResult", {}).get("queryText", "").strip().lower()

    # 從 Google 試算表讀取 FAQ
    sheet = client.open_by_key(SPREADSHEET_ID).sheet1
    data = sheet.get_all_values()

    # 將 FAQ 儲存成字典，問題為 key，回答為 value
    faq_dict = {row[0].strip().lower(): row[1] for row in data[1:] if len(row) >= 2}

    # 根據問題返回答案
    answer = faq_dict.get(question, "抱歉，我找不到相關資訊。")

    # 回應給 Dialogflow
    response = {
        "fulfillmentText": answer
    }
    return jsonify(response)


if __name__ == "__main__":
    app.run(debug=True)
