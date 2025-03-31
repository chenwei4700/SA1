from flask import Flask, request, jsonify, render_template
import google.generativeai as genai
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

# 設定 Google Sheets API
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("api.json", scope)
client = gspread.authorize(creds)

# 開啟指定的試算表和工作表
sheet_id = "1C_qYknxD84tMd3yAFMmYepNHa2raJJXEbp8ZL01HeMc"  # 替換為您的試算表 ID
sheet = client.open_by_key(sheet_id).sheet1

# 設定 Gemini API
genai.configure(api_key="AIzaSyBKl0pZ7wpCju8ZSTJLAX8ViJzldGlDxBs")  # 替換為你的 Gemini API Key

# 收集所有相關問題與答案
def collect_similar_answers(question):
    data = sheet.get_all_records()
    collected_responses = []
    
    for row in data:
        if question.strip() in row["問題"].strip():
            collected_responses.append(f"問題：{row['問題']}\n回答：{row['回答']}")
    
    return "\n\n".join(collected_responses) if collected_responses else "抱歉，我找不到相關的答案。"

# 使用 Gemini 整理回答
def get_gemini_response(context):
    model = genai.GenerativeModel('gemini-2.0-flash')
    chat = model.start_chat(history=[])
    response = chat.send_message(
        f"你是一個幫助學生整理資訊的AI助理，請根據以下資料提供清楚明確的回答：\n{context}"
    )
    return response.text.strip()

@app.route('/')
def index():
    return render_template('chat.html')

@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json()
    if not data or "question" not in data:
        return jsonify({"error": "缺少必要的參數"}), 400

    question = data["question"]
    print(f"收到問題：{question}")

    # 收集所有相關回答
    collected_info = collect_similar_answers(question)
    print(f"收集到的資訊：\n{collected_info}")

    # 交給 Gemini 整理答案
    final_answer = get_gemini_response(collected_info)
    print(f"Gemini 整理後答案：{final_answer}")

    return jsonify({"response": f"問題：{question}\n回答：{final_answer}"})

@app.route('/clear_history', methods=['POST'])
def clear_history():
    # 這裡你可以選擇清除聊天紀錄的方式
    # 比如：不做後端處理，單純清除畫面
    return jsonify({"message": "對話紀錄已清除"}), 200

if __name__ == '__main__':
    app.run(debug=True)
