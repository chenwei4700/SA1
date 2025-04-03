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
genai.configure(api_key="AIzaSyBKl0pZ7wpCju8ZSTJLAX8ViJzldGlDxBs")

def load_synonyms_from_db():
    """
    從資料庫加載同義詞字典
    """
    try:
        # 獲取同義詞工作表
        synonym_sheet = client.open_by_key(sheet_id).worksheet("同義詞")
        synonym_data = synonym_sheet.get_all_records()
        
        # 構建同義詞字典
        synonyms = {}
        for row in synonym_data:
            keyword = row.get("關鍵詞", "").strip()
            if keyword:
                synonym_list = [s.strip() for s in row.get("同義詞", "").split(",") if s.strip()]
                if synonym_list:
                    synonyms[keyword] = synonym_list
                    # 為每個同義詞也添加反向映射
                    for syn in synonym_list:
                        if syn not in synonyms:
                            synonyms[syn] = [keyword]
                        else:
                            if keyword not in synonyms[syn]:
                                synonyms[syn].append(keyword)
        
        return synonyms
    except Exception as e:
        print(f"加載同義詞時發生錯誤: {str(e)}")
        # 返回默認同義詞字典
        return {
            "教師": ["老師", "師長"],
            "老師": ["教師", "師長"]
        }

# 在應用啟動時加載同義詞
synonyms = load_synonyms_from_db()

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
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'#模擬瀏覽器，防止網站阻擋爬蟲請求。
        }
        response = requests.get(url, headers=headers, timeout=10)#發送一個 HTTP GET 請求到 url，讓請求帶上 User-Agent，避免被網站識別為爬蟲並封鎖，設定 最大等待時間 為 10 秒，避免伺服器回應過慢而導致程式卡住
        response.encoding = 'utf-8'#設定編碼為utf-8，確保爬取的內容能正確解碼
        soup = BeautifulSoup(response.text, 'html.parser')#使用 BeautifulSoup 解析 HTML：方便提取標籤、文字、連結等內容。
        #解析速度快（比 html5lib 快，但比 lxml 慢）。能自動修正 HTML 結構，適合解析不完整的 HTML。 html.parser 是 Python 內建的 HTML 解析器

        # 清理網頁內容
        for script in soup(["script", "style"]):
            script.decompose()#刪除 script 和 style 標籤，這些標籤通常包含 JavaScript 和 CSS 代碼，不包含實際的內容
        text = soup.get_text(separator='\n', strip=True)#提取純文字內容，separator='\n' 表示以換行符號分隔文本，strip=True 表示去除前後的空白字符
        lines = [line.strip() for line in text.split('\n') if line.strip()]#將文本按換行符號分割成行，並去除每行前後的空白字符
        
        return '\n'.join(lines)[:3000]  # 限制內容長度為3000字
    except Exception as e:
        print(f"爬取網頁時發生錯誤: {str(e)}")
        return None

def fetch_pdf_content(url):
    """
    爬取 PDF 文件的內容
    參數：
        url: PDF 文件的 URL
    返回：
        PDF 文件的文本內容，如果失敗則返回 None
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=20)  # PDF 可能較大，增加超時時間
        
        if response.status_code != 200:
            print(f"下載 PDF 失敗，狀態碼: {response.status_code}")
            return None
            
        # 將 PDF 內容讀入記憶體
        pdf_file = io.BytesIO(response.content)
        
        try:
            # 使用 PyPDF2 讀取 PDF
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            
            # 提取每一頁的文本
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n\n"
                
            # 清理文本
            text = text.strip()
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            return '\n'.join(lines)[:5000]  # 限制內容長度為 5000 字
            
        except Exception as e:
            print(f"解析 PDF 時發生錯誤: {str(e)}")
            return None
            
    except Exception as e:
        print(f"下載 PDF 時發生錯誤: {str(e)}")
        return None

def is_pdf_url(url):
    """
    檢查 URL 是否指向 PDF 文件
    參數：
        url: 要檢查的 URL
    返回：
        布爾值，表示是否為 PDF URL
    """
    return url.lower().endswith('.pdf')

def fetch_and_save_content(url):
    """
    根據 URL 類型爬取內容並保存到工作表2
    參數：
        url: 要爬取的 URL
    返回：
        處理後的內容，如果失敗則返回 None
    """
    try:
        content = None
        
        # 根據 URL 類型選擇不同的爬取方法
        if is_pdf_url(url):
            content = fetch_pdf_content(url)
            content_type = "PDF 內容"
        else:
            content = fetch_webpage_content(url)
            content_type = "網頁內容"
            
        if content:
            # 將內容保存到工作表2
            chat_sheet.append_row([
                str(datetime.now()),  # 記錄時間
                url,                  # 記錄 URL
                content               # 記錄內容
            ])
            return f"{content_type}：\n{content}"
    except Exception as e:
        print(f"儲存內容時發生錯誤: {str(e)}")
    return None

def search_cached_content(question):
    """
    在工作表2中搜索與問題相關的暫存內容
    參數：
        question: 用戶的問題
    返回：
        相關的暫存內容，如果沒有找到則返回 None
    """
    try:
        cached_data = chat_sheet.get_all_records()#獲取工作表2中的所有記錄，串列包字典，方便找
        relevant_contents = []
        
        for row in cached_data:
            content = row.get('網頁內容', '')  # 取得 "網頁內容" 欄位，如果不存在則給空字串 ''
            if content and question.lower() in content.lower():  # 檢查內容是否包含 question（忽略大小寫）
                relevant_contents.append(f"相關網頁內容：\n{content}")  # 儲存符合條件的內容

        return "\n\n".join(relevant_contents) if relevant_contents else None  # 回傳找到的內容，否則回傳 None

    except Exception as e:
        print(f"查詢快取內容時發生錯誤: {str(e)}")
        return None

def clear_cached_content():
    """
    清除工作表2中的暫存內容，但保留標題行
    """
    try:
        # 保存標題行
        headers = chat_sheet.row_values(1)
        # 清除所有內容
        chat_sheet.clear()
        # 重新寫入標題行
        chat_sheet.update('A1:C1', [headers])
        print("已清除暫存的網頁內容")
    except Exception as e:
        print(f"清除快取內容時發生錯誤: {str(e)}")

def expand_query_with_synonyms(question):
    """
    擴展查詢，加入同義詞
    參數：
        question: 原始問題
    返回：
        包含同義詞的擴展問題列表
    """
    expanded_queries = [question]
    words = question.lower().split()
    
    for word in words:
        # 檢查這個詞是否有同義詞
        if word in synonyms:
            for synonym in synonyms[word]:
                # 創建一個新的查詢，將原詞替換為同義詞
                new_query = question.lower().replace(word, synonym)
                expanded_queries.append(new_query)
    
    return expanded_queries

def analyze_question_intent(question):
    """
    使用 Gemini 分析問題意圖，提取關鍵詞和同義詞
    參數：
        question: 用戶的原始問題
    返回：
        包含關鍵詞和同義詞的字典
    """
    model = genai.GenerativeModel('gemini-2.0-flash')
    
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
    
    try:
        response = model.generate_content(prompt)
        result = response.text.strip()
        
        # 提取JSON部分
        import json
        import re
        json_match = re.search(r'({.*})', result, re.DOTALL)
        if json_match:
            result = json_match.group(1)
            
        intent_data = json.loads(result)
        return intent_data
    except Exception as e:
        print(f"分析問題意圖時發生錯誤: {str(e)}")
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
    參數：
        question: 用戶的問題
    返回：
        整理後的答案文本
    """
    # 先查詢暫存內容
    cached_content = search_cached_content(question)
    if cached_content:
        return cached_content
    
    # 使用 Gemini 分析問題意圖
    intent_data = analyze_question_intent(question)
    print(f"問題意圖分析結果: {intent_data}")
    
    # 從 FAQ 表中查詢
    data = faq_sheet.get_all_records()
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
            
            # 處理答案中的 URL（支持網頁和 PDF）
            for word in words:
                if is_url(word):
                    content = fetch_and_save_content(word)  # 使用新的統一函數
                    if content:
                        content_results.append(content)
            
            # 組合答案
            full_response = f"問題：{row['問題']}\n回答：{answer}"
            if content_results:
                full_response += "\n\n" + "\n\n".join(content_results)
            
            collected_responses.append(full_response)
    
    return "\n\n---\n\n".join(collected_responses) if collected_responses else "抱歉，我找不到相關的答案。"

# 修改 Gemini 回應函數
def get_gemini_response(context, question):
    model = genai.GenerativeModel('gemini-2.0-flash')
    chat = model.start_chat(history=[])
    
    # 獲取歷史對話和相關URL
    history = session.get('chat_history', [])
    prev_urls = session.get('prev_urls', [])
    
    # 重播歷史對話
    for prev_msg in history:
        chat.send_message(prev_msg['content'])
    
    # 如果有之前的URL，重新爬取內容
    additional_context = ""
    if prev_urls:
        webpage_contents = []
        for url in prev_urls:
            content = fetch_webpage_content(url)
            if content:
                webpage_contents.append(f"相關網頁內容：\n{content}")
        if webpage_contents:
            additional_context = "\n\n相關歷史網頁內容：\n" + "\n\n".join(webpage_contents)
    
    prompt = f"""
你是一個專業的教育助理。請根據以下資料、歷史對話和相關網頁內容，針對問題「{question}」提供一個完整且具體的回答。
如果資料中包含網頁內容，請特別注意整合這些資訊來回答問題。
請確保回答：
1. 直接回應問題重點
2. 條理分明
3. 如果有相關的網頁資訊，請整合進回答中
4. 考慮歷史對話的上下文

以下是相關資料：
{context}
{additional_context}
"""
    response = chat.send_message(prompt)
    return response.text.strip()

# 儲存對話記錄到 Google Sheets
def save_chat_history(question, answer):
    try:
        chat_sheet.append_row([
            str(datetime.now()),  # 時間戳
            question,
            answer
        ])
    except Exception as e:
        print(f"儲存對話記錄時發生錯誤: {str(e)}")

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

    # 重置計時器
    session.permanent = True
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 檢查是否需要清除歷史
    if 'last_activity' in session:
        last_activity = datetime.strptime(session['last_activity'], '%Y-%m-%d %H:%M:%S')
        if (datetime.now() - last_activity).seconds > 180:
            clear_cached_content()  # 清除工作表2的內容
            session['chat_history'] = []
    else:
        session['chat_history'] = []

    # 更新最後活動時間
    session['last_activity'] = current_time

    # 使用基於意圖的方法收集答案
    collected_info = collect_similar_answers_with_intent(question)
    print(f"收集到的資訊：\n{collected_info}")

    # 交給 Gemini 整理答案
    final_answer = get_gemini_response(collected_info, question)
    print(f"Gemini 整理後答案：{final_answer}")

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

# 添加清除對話歷史的端點
@app.route('/clear_history', methods=['POST'])
def clear_history():
    # 清除 session
    session['chat_history'] = []
    # 清除工作表2的內容
    clear_cached_content()
    return jsonify({"message": "對話歷史已清除"})

if __name__ == '__main__':
    app.run(debug=True)
