"""
這是一個基於 Flask 的聊天機器人應用，整合了以下功能：
1. Google Sheets 工左表1作為數據存儲，工作表2作為對話儲存
2. Gemini AI 作為對話引擎
3. 網頁爬蟲功能
4. 對話歷史記錄管理
"""

from flask import Flask, request, jsonify, render_template, session
import google.generativeai as genai#Gemini AI
import gspread#Google Sheets
from oauth2client.service_account import ServiceAccountCredentials#Google Sheets
import requests
from bs4 import BeautifulSoup#爬蟲
from urllib.parse import urlparse
from datetime import datetime, timedelta
import io
import PyPDF2
import json
import re
import logging

# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# 初始化 Flask 應用
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # 用於加密 session 數據
app.permanent_session_lifetime = timedelta(minutes=3)  # session 有效期為 3 分鐘

# 設定 Google Sheets API 訪問權限
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("api.json", scope)
client = gspread.authorize(creds)#授權客戶端打開google sheets

# 連接到指定的 Google Sheets
sheet_id = "1C_qYknxD84tMd3yAFMmYepNHa2raJJXEbp8ZL01HeMc"  # Google Sheets 的 ID
faq_sheet = client.open_by_key(sheet_id).sheet1  # 第一個工作表存儲 FAQ
chat_sheet = client.open_by_key(sheet_id).worksheet("工作表2")  # 第二個工作表存儲暫存的網頁內容

# 設定 Gemini AI
# 使用最新的模型名称
GEMINI_API_KEY = "AIzaSyCvD1yTiWA3EljhiSxMLklTcniv2PVAQ_k"
genai.configure(api_key=GEMINI_API_KEY)

def is_url(string):
    """
    檢查字符串是否為有效的 URL
    參數：
        string: 要檢查的字符串
    返回：
        布爾值，表示是否為有效 URL
    """
    try:
        result = urlparse(string)
        return all([result.scheme, result.netloc])#撿查是否為有效的(協議，網域)
    except:
        return False

def fetch_webpage_content(url):
    """
    爬取指定 URL 的網頁內容
    參數：
        url: 要爬取的網頁地址
    返回：
        處理後的網頁文本內容，如果失敗則返回 None
    """
    try:
        if not is_url(url):
            return ""
            
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        content_type = response.headers.get('Content-Type', '').lower()
        
        # 處理 PDF
        if 'application/pdf' in content_type:
            try:
                with io.BytesIO(response.content) as f:
                    reader = PyPDF2.PdfReader(f)
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text() + "\n"
                    return text[:2000]  # 限制內容長度
            except Exception as e:
                logger.error(f"處理 PDF 文件時發生錯誤: {str(e)}")
                return ""
        
        # 處理網頁
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 移除不需要的元素
        for script in soup(["script", "style", "meta", "link", "head"]):
            script.extract()
            
        # 提取主要內容
        main_content = soup.get_text(separator='\n', strip=True)
        
        # 保存到暫存表中
        save_webpage_content(url, main_content[:1000])  # 限制長度
        
        return main_content[:2000]  # 限制返回內容長度
    except Exception as e:
        logger.error(f"獲取網頁內容時發生錯誤: {str(e)}")
        return ""

def save_webpage_content(url, content):
    """
    保存網頁內容到 Google Sheets
    參數：
        url: 網頁地址
        content: 網頁內容
    """
    try:
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        chat_sheet.append_row([current_time, url, content[:1000]])  # 限制長度
    except Exception as e:
        logger.error(f"保存網頁內容時發生錯誤: {str(e)}")

def search_cached_content(query):
    """
    搜索暫存的網頁內容
    參數：
        query: 用戶的問題
    返回：
        相關的暫存內容，如果沒有找到則返回 None
    """
    try:
        records = chat_sheet.get_all_records()
        for record in records:
            if 'URL' in record and query.lower() in record.get('URL', '').lower():
                return record.get('Content', '')
        return ""
    except Exception as e:
        logger.error(f"搜索暫存內容時發生錯誤: {str(e)}")
        return ""

def clear_cached_content():
    """
    清除暫存的網頁內容
    """
    try:
        # 保留標題行
        chat_sheet.delete_rows(2, chat_sheet.row_count)
    except Exception as e:
        logger.error(f"清除暫存內容時發生錯誤: {str(e)}")

def analyze_question_intent(question):
    """
    使用 Gemini 分析問題意圖，提取關鍵詞和同義詞
    參數：
        question: 用戶的原始問題
    返回：
        包含關鍵詞和同義詞的字典
    """
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')  # 更新為最新的模型名稱
        
        prompt = f"""
分析以下問題的意圖和關鍵詞："{question}"

請提取：
1. 主要意圖（例如：查詢、申請、了解流程等）
2. 關鍵詞（最多5個）
3. 每個關鍵詞的可能同義詞（最多3個）

以JSON格式回答，格式如下：
{{
  "intent": "意圖描述",
  "keywords": [
    {{
      "word": "關鍵詞1",
      "synonyms": ["同義詞1", "同義詞2", "同義詞3"]
    }},
    {{
      "word": "關鍵詞2",
      "synonyms": ["同義詞1", "同義詞2"]
    }}
  ]
}}

只返回JSON，不要有其他文字。
"""
        
        response = model.generate_content(prompt)
        result = response.text.strip()
        
        # 提取JSON部分
        json_match = re.search(r'({.*})', result, re.DOTALL)
        if json_match:
            result = json_match.group(1)
            
        intent_data = json.loads(result)
        return intent_data
    except Exception as e:
        logger.error(f"分析問題意圖時發生錯誤: {str(e)}", exc_info=True)
        # 返回基本分析結果
        return {
            "intent": "查詢",
            "keywords": [
                {
                    "word": question,
                    "synonyms": []
                }
            ]
        }

def collect_similar_answers_with_intent(question):
    """
    基於意圖分析收集與問題相關的答案
    """
    try:
        # 先查詢暫存內容
        cached_content = search_cached_content(question)
        if cached_content:
            return cached_content
        
        # 使用 Gemini 分析問題意圖
        intent_data = analyze_question_intent(question)
        print(f"問題意圖分析結果: {intent_data}")
        
        # 直接获取所有值并手动解析，避免表头问题
        try:
            all_values = faq_sheet.get_all_values()
            if not all_values or len(all_values) < 2:  # 检查是否有数据
                return "抱歉，找不到相關回答。(FAQ表格為空)"
                
            # 假设第一列是问题，第二列是答案
            question_col = 0
            answer_col = 1
            
            # 构建数据列表
            data = []
            for row in all_values[1:]:  # 跳过表头行
                if len(row) > answer_col:  # 确保行有足够的列
                    data.append({
                        "問題": row[question_col],
                        "回答": row[answer_col]
                    })
        except Exception as e:
            print(f"獲取FAQ數據時發生錯誤: {str(e)}")
            return "抱歉，系統查詢失敗。(獲取FAQ數據時出錯)"
            
        collected_responses = []
        
        # 構建搜索關鍵詞列表
        search_terms = [question.lower()]  # 原始問題
        
        # 添加從意圖分析中提取的關鍵詞和同義詞
        for keyword_data in intent_data.get("keywords", []):
            word = keyword_data.get("word", "").lower()
            if word and word not in search_terms:
                search_terms.append(word)
            
            for synonym in keyword_data.get("synonyms", []):
                if synonym.lower() not in search_terms:
                    search_terms.append(synonym.lower())
        
        print(f"搜索關鍵詞: {search_terms}")
        
        # 搜索匹配的答案
        for row in data:
            question_text = row["問題"].lower()
            
            # 檢查是否有任何關鍵詞匹配
            matched = False
            for term in search_terms:
                if term in question_text:
                    matched = True
                    break
            
            if matched:
                answer = row["回答"]
                words = answer.split()
                content_results = []
                
                # 處理答案中的 URL
                for word in words:
                    if is_url(word):
                        content = fetch_webpage_content(word)
                        if content:
                            content_results.append(f"來自 {word} 的內容：\n{content}")
                
                # 組合答案
                full_response = f"問題：{row['問題']}\n回答：{answer}"
                if content_results:
                    full_response += "\n\n" + "\n\n".join(content_results)
                
                collected_responses.append(full_response)
        
        return "\n\n---\n\n".join(collected_responses) if collected_responses else "抱歉，找不到相關回答。"
    except Exception as e:
        print(f"收集答案時發生錯誤: {str(e)}")
        return f"抱歉，系統查詢失敗。錯誤信息: {str(e)}"

# 修改 Gemini 回應函數
def get_gemini_response(context, question):
    """
    使用 Gemini 生成答案
    """
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')  # 更新為最新的模型名稱
        
        prompt = f"""
你是一個專業的教育助理。請根據以下資料，針對問題「{question}」提供一個完整且具體的回答。
如果資料中包含網頁內容，請特別注意整合這些資訊來回答問題。
請確保回答：
1. 直接回應問題重點
2. 條理分明
3. 如果有相關的網頁資訊，請整合進回答中

以下是相關資料：
{context}
"""
        
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        logger.error(f"生成 Gemini 回答時發生錯誤: {str(e)}", exc_info=True)
        return "抱歉，我現在無法處理您的請求。請稍後再試。"

# 儲存對話記錄到 Google Sheets
def save_chat_history(question, answer):
    try:
        chat_sheet.append_row([
            str(datetime.now()),  # 時間戳
            question,
            answer
        ])
    except Exception as e:
        logger.error(f"儲存對話記錄時發生錯誤: {str(e)}")

@app.route('/')
def index():
    return render_template('chat.html')

@app.route('/ask', methods=['POST'])
def ask():
    try:
        logger.debug("收到新的請求")
        data = request.get_json()
        if not data or "question" not in data:
            return jsonify({"error": "缺少必要的參數"}), 400

        question = data["question"].strip()
        if not question:
            return jsonify({"error": "問題不能為空"}), 400

        logger.debug(f"收到問題：{question}")

        # 重置計時器
        session.permanent = True
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 檢查是否需要清除歷史
        if 'last_activity' in session:
            last_activity = session['last_activity']
            if isinstance(last_activity, str):
                last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if (datetime.now() - last_activity).seconds > 180:
                clear_cached_content()
                session['chat_history'] = []
        else:
            session['chat_history'] = []

        # 更新最後活動時間
        session['last_activity'] = current_time

        # 使用基於意圖的方法收集答案
        collected_info = collect_similar_answers_with_intent(question)
        logger.debug(f"收集到的信息：{collected_info[:100]}...")  # 只記錄前100個字符

        # 交給 Gemini 整理答案
        final_answer = get_gemini_response(collected_info, question)
        logger.debug(f"Gemini 整理後答案：{final_answer[:100]}...")  # 只記錄前100個字符

        # 更新對話歷史
        session['chat_history'].append({
            'role': 'user',
            'content': question
        })
        session['chat_history'].append({
            'role': 'assistant',
            'content': final_answer
        })

        session.modified = True

        return jsonify({
            "response": f"問題：{question}\n回答：{final_answer}",
            "history": session['chat_history']
        })
    except Exception as e:
        logger.error(f"處理請求時發生錯誤: {str(e)}", exc_info=True)
        return jsonify({
            "error": "伺服器內部錯誤",
            "details": str(e)
        }), 500

# 添加清除對話歷史的端點
@app.route('/clear_history', methods=['POST'])
def clear_history():
    try:
        clear_cached_content()
        session.clear()
        return jsonify({"message": "歷史記錄已清除"})
    except Exception as e:
        logger.error(f"清除歷史記錄時發生錯誤: {str(e)}", exc_info=True)
        return jsonify({"error": "清除歷史記錄失敗"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
