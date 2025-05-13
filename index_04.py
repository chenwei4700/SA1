from flask import Flask, render_template, request, redirect, session, flash
import mysql.connector
import os
import re
from werkzeug.utils import secure_filename
from datetime import datetime
from post_02 import post_bp
#from ge import app

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
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'#模擬瀏覽器，防止網站阻擋爬蟲請求。
        }
        response = requests.get(url, headers=headers, timeout=10)#發送一個 HTTP GET 請求到 url，讓請求帶上 User-Agent，避免被網站識別為爬蟲並封鎖，設定 最大等待時間 為 10 秒，避免伺服器回應過慢而導致程式卡住
        response.raise_for_status()#如果 HTTP 請求返回的狀態碼不是 200，則會引發一個 HTTPError 異常
        
        content_type = response.headers.get('Content-Type', '').lower()#獲取 HTTP 響應頭中的 Content-Type 值，並將其轉換為小寫
        
        # 處理 PDF
        if 'application/pdf' in content_type:
            try:
                with io.BytesIO(response.content) as f:#將 response.content 轉換為 BytesIO 對象，這樣可以方便地進行 PDF 文件的讀取和處理
                    reader = PyPDF2.PdfReader(f)#使用 PyPDF2 庫讀取 PDF 文件
                    text = ""
                    for page in reader.pages:#遍歷 PDF 文件的每一頁，並將每頁的文字內容添加到 text 字串中
                        text += page.extract_text() + "\n"#使用 PyPDF2 的 extract_text() 方法提取每頁的文字內容，並將其添加到 text 字串中，每頁之間用換行符分隔
                    return text[:2000]  # 限制內容長度
            except Exception as e:
                logger.error(f"處理 PDF 文件時發生錯誤: {str(e)}")#是 logging 模組裡用來記錄「錯誤等級」（error level）的訊息。
                return ""
        
        # 處理網頁
        soup = BeautifulSoup(response.text, 'html.parser')#使用 BeautifulSoup 解析 HTML：方便提取標籤、文字、連結等內容。
        #解析速度快（比 html5lib 快，但比 lxml 慢）。能自動修正 HTML 結構，適合解析不完整的 HTML。 html.parser 是 Python 內建的 HTML 解析器
        
        # 移除不需要的元素
        for script in soup(["script", "style", "meta", "link", "head"]):
            script.extract()#刪除 script 和 style 標籤，這些標籤通常包含 JavaScript 和 CSS 代碼，不包含實際的內容
            
        # 提取主要內容
        main_content = soup.get_text(separator='\n', strip=True)#提取純文字內容，separator='\n' 表示以換行符號分隔文本，strip=True 表示去除前後的空白字符
        
        # 保存到暫存表中
        save_webpage_content(url, main_content[:1000])  #   限制長度
        
        return main_content[:2000]  # 限制返回內容長度
    except Exception as e:
        logger.error(f"獲取網頁內容時發生錯誤: {str(e)}")#是 logging 模組裡用來記錄「錯誤等級」（error level）的訊息。
        return ""

def save_webpage_content(url, content):
    """
    保存網頁內容到 Google Sheets
    參數：
        url: 網頁地址
        content: 網頁內容
    """
    try:
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')#獲取當前時間，並將其格式化為字串
        chat_sheet.append_row([current_time, url, content[:1000]])  # 限制長度
    except Exception as e:
        logger.error(f"保存網頁內容時發生錯誤: {str(e)}")

def search_cached_content(query):
    """
    搜索暫存的網頁內容
    參數：
        query: 用戶的問題
    返回：
        相關的暫存內容，如果沒有找到則返回空字符串
    """
    if not query:
        return ""
        
    try:
        # 首先获取工作表的所有值，包括标题行
        all_values = chat_sheet.get_all_values()
        
        # 确保有数据
        if not all_values or len(all_values) <= 1:
            return ""
        
        # 获取标题行
        headers = all_values[0]
        
        # 找出URL和网页内容列的索引
        url_index = -1
        content_index = -1
        
        for i, header in enumerate(headers):#用 enumerate() 同時獲取列表 headers 中每個元素的索引 i 和內容 header。
            if header and ('url' in header.lower() or 'URL' in header):
                url_index = i
            elif header and ('content' in header.lower() or '内容' in header or '內容' in header):
                content_index = i
        
        # 如果找不到所需的列，返回空字符串
        if url_index == -1 or content_index == -1:
            # 打印列名以便调试
            logger.error(f"找不到所需的列，工作表标题行: {headers}")
            return ""
        
        # 遍历数据行
        for row in all_values[1:]:#從第二行開始遍歷，跳過表頭
            if len(row) <= max(url_index, content_index):#
                continue  # 跳過數據不完整的行
                
            url = row[url_index]#獲取 URL 列的值
            content = row[content_index] if len(row) > content_index else ""#獲取網頁內容列的值
            
            # 检查URL是否匹配查询
            if url and isinstance(url, str) and query.lower() in url.lower():
                return content if content else ""
        
        return ""
    except Exception as e:
        logger.error(f"搜索暫存內容時發生錯誤: {str(e)}")
        return ""

def clear_cached_content():
    """
    清除暫存的網頁內容 - 更安全的方法
    """
    try:
        # 获取标题行（如果存在）
        headers = []
        try:
            all_values = chat_sheet.get_all_values()
            if all_values and len(all_values) > 0:
                headers = all_values[0]#獲取表頭
        except Exception:
            # 如果无法获取标题行，使用默认标题
            headers = ["時間", "URL", "網頁內容"]
        
        # 清空整个工作表
        chat_sheet.clear()
        
        # 如果有标题行，则重新添加
        if headers:
            chat_sheet.append_row(headers)
            logger.info(f"已清空暫存表並重新添加標題行: {headers}")
        else:
            logger.info("已清空暫存表")
    except Exception as e:
        logger.error(f"清除暫存內容時發生錯誤: {str(e)}")

def analyze_question_intent(question):
    """
    使用 Gemini 分析問題意圖，提取關鍵詞和同義詞
    參數：
        question: 用戶的原始問題
    返回：
        包含關鍵詞和同義詞的字典，以及是否與資管系課業相關的標記
    """
    try:
        model = genai.GenerativeModel('gemini-2.0-flash-thinking-exp-01-21')  # 使用正確的模型名稱
        fap_info = faq_sheet.get_all_values()
        # 首先判斷問題是否與資管系課業相關
        relevance_prompt = f"""
判斷以下問題是否與資管系(資訊管理系)的課業或學術內容相關：
問題："{question}"

請分析這個問題是否與以下資訊有關：


1.{fap_info}
只回答 "相關" 或 "不相關"，不要有其他文字。
"""
        
        relevance_response = model.generate_content(relevance_prompt)
        relevance_result = relevance_response.text.strip().lower()
        
        # 判斷是否相關
        is_relevant = "相關" in relevance_result and "不相關" not in relevance_result
        
        # 如果不相關，直接返回
        if not is_relevant:
            return {
                "intent": "非課業相關",
                "keywords": [],
                "is_relevant": False
            }
        
        # 如果相關，繼續進行關鍵詞分析
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
        json_match = re.search(r'({.*})', result, re.DOTALL)#加了 re.DOTALL 之後，就可以抓多行的資料，例如多行 JSON 或函數內容。search() 是用來搜尋第一個符合條件的子字串，如果找到會回傳一個 match 物件，找不到就回傳 None。


        if json_match:
            result = json_match.group(1)
            
        intent_data = json.loads(result)#將 result 轉換為 Python 的 JSON 格式
        intent_data["is_relevant"] = True  # 添加相關性標記
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
            ],
            "is_relevant": True  # 預設為相關
        }

def collect_similar_answers_with_intent(question):
    """
    基於意圖分析收集與問題相關的答案
    參數：
        question: 用戶的問題
    返回：
        整理後的答案文本
    """
    try:
        # 先查詢暫存內容
        cached_content = search_cached_content(question)
        if cached_content:
            return cached_content
        
        # 使用 Gemini 分析問題意圖
        intent_data = analyze_question_intent(question)
        print(f"問題意圖分析結果: {intent_data}")
        
        # 檢查問題是否與資管系課業相關
        if intent_data.get("is_relevant") == False:
            return "抱歉，我只能回答與資管系課業相關的問題。您的問題似乎與資管系課業無關。"
        
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
                    question_text = row[question_col] if row[question_col] else ""
                    answer_text = row[answer_col] if row[answer_col] else ""
                    data.append({
                        "問題": question_text,
                        "回答": answer_text
                    })
        except Exception as e:
            print(f"獲取FAQ數據時發生錯誤: {str(e)}")
            return "抱歉，系統查詢失敗。(獲取FAQ數據時出錯)"
            
        collected_responses = []
        
        # 構建搜索關鍵詞列表，使用空格分隔的单词作为关键词
        search_terms = []
        for word in question.lower().split():
            if word and len(word) >= 2:  # 忽略太短的词
                search_terms.append(word)
        
        # 添加從意圖分析中提取的關鍵詞和同義詞
        for keyword_data in intent_data.get("keywords", []):
            word = keyword_data.get("word")
            if word and isinstance(word, str):#
                word = word.lower()
                if word not in search_terms:
                    search_terms.append(word)
            
            synonyms = keyword_data.get("synonyms", [])
            if synonyms and isinstance(synonyms, list):
                for synonym in synonyms:
                    if synonym and isinstance(synonym, str):
                        synonym = synonym.lower()
                        if synonym not in search_terms:
                            search_terms.append(synonym)
        
        print(f"搜索關鍵詞: {search_terms}")
        
        # 搜索匹配的答案
        for row in data:
            question_text = row.get("問題", "").lower()
            
            # 檢查是否有任何關鍵詞匹配
            matched = False
            for term in search_terms:
                if term and question_text and term in question_text:
                    matched = True
                    break
            
            if matched:
                answer = row.get("回答", "")
                if not answer:
                    continue  # 跳过空答案
                    
                words = answer.split()
                content_results = []
                
                # 處理答案中的 URL
                for word in words:
                    if word and is_url(word):
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
    使用 Gemini 生成回答
    參數：
        context: 收集到的相關資訊
        question: 原始問題
    返回：
        整理後的回答
    """
    try:
        # 檢查是否已經判斷為不相關的問題
        if "抱歉，我只能回答與資管系課業相關的問題" in context:
            return context
            
        model = genai.GenerativeModel('gemini-2.0-flash')  # 使用正確的模型名稱
        
        prompt = f"""
你是一個專業的資管系教育助理。請根據以下資料，針對問題「{question}」提供一個完整且具體的回答。
如果資料中包含網頁內容，請特別注意整合這些資訊來回答問題。
請確保回答：
1. 直接回應問題重點
2. 條理分明
3. 如果有相關的網頁資訊，請整合進回答中，並在最後附上網頁連結 
4. 如果問題與資管系課業無關，請委婉拒絕並說明你只能回答與資管系課業相關的問題


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
    """
    將對話記錄儲存到 Google Sheets
    參數：
        question: 用戶問題
        answer: 系統回答
    """
    try:
        chat_sheet.append_row([
            str(datetime.now()),  # 時間戳
            question,
            answer
        ])
    except Exception as e:
        logger.error(f"儲存對話記錄時發生錯誤: {str(e)}")

#@app.route('/')
#def index():
    """
    渲染聊天頁面
    """
    #return render_template('chat.html')

@app.route('/ask', methods=['POST'])
def ask():
    """
    處理用戶提問並返回回答
    """
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
                clear_cached_content()#清除工作表2的內容
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
        session['chat_history'] = session.get('chat_history', [])
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
    """
    清除對話歷史和暫存內容
    """
    try:
        clear_cached_content()
        session.clear()
        return jsonify({"message": "歷史記錄已清除"})
    except Exception as e:
        logger.error(f"清除歷史記錄時發生錯誤: {str(e)}", exc_info=True)
        return jsonify({"error": "清除歷史記錄失敗"}), 500


#app = Flask(__name__)
#app.secret_key = 'your_secret_key'


# ✅ 註冊交流區 blueprint
app.register_blueprint(post_bp, url_prefix='/post')

# ✅ MySQL 資料庫連線

def get_db_connection():
    return mysql.connector.connect(
        user='root',
        password='',
        database='SA2-2',
        unix_socket='/Applications/XAMPP/xamppfiles/var/mysql/mysql.sock'
    )

# ✅ 上傳檔案設定
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'heic'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ✅ 首頁（登入頁）
@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def do_login():
    if request.method == 'POST':
        # 只有表單送出（POST）才讀取帳號密碼
        account = request.form['account']
        password = request.form['password']

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT * FROM Users WHERE account = %s AND password = %s", (account, password))
        user = cur.fetchone()

        if user:
            session['user'] = account                # 備用
            session['user_id'] = user[0]            # ✅ 使用 user_id 作為外鍵依據
            session['name'] = user[3]
            session['role'] = user[4]
            session['nickname'] = user[5]  


            # ✅ 查詢最新頭像（images.user_id FK 連接 Users.user_id）
            cur.execute("""
                SELECT file_path
                FROM images
                WHERE user_id = %s
                ORDER BY uploadtime DESC
                LIMIT 1
            """, (user[0],))
            img = cur.fetchone()

            session['avatar'] = img[0] if img else 'images/avatar.png'

            cur.close()
            conn.close()
            return redirect('/dashboard')
        else:
            cur.close()
            conn.close()
            flash('登入失敗，請檢查帳號或密碼')
            return redirect('/login')
    else:
        return render_template('login.html')

# ✅ 登出
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# ✅ 主頁（dashboard）
@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        return render_template('main.html', name=session['name'], avatar=session['avatar'])
    else:
        return redirect('/')

# ✅ 註冊新帳號
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        account = request.form['account']
        password = request.form['password']
        name = request.form['name']
        nickname = request.form.get('nickname', '')
        

        if not re.match(r'^\d{9}@fju\.edu\.tw$', account):
            flash('帳號必須是9位數字+@fju.edu.tw的格式')
            return redirect('/register')

        if len(password) < 6 or len(password) > 20:
            flash('密碼長度必須在6到20字之間')
            return redirect('/register')

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT * FROM Users WHERE account = %s", (account,))
        existing_user = cur.fetchone()

        if existing_user:
            cur.close()
            conn.close()
            flash('帳號已存在，請使用其他帳號')
            return redirect('/register')

        # ✅ 插入新使用者
        cur.execute("""
            INSERT INTO Users (account, password, user_name, role, nickname)
            VALUES (%s, %s, %s, 'U',%s)
        """, (account, password, name, nickname))
        conn.commit()

        cur.close()
        conn.close()

        flash('註冊成功！請登入')
        return redirect('/login')

    return render_template('register.html')


# ✅ 修改名字＋修改暱稱+上傳頭像（合併版）
@app.route('/update_profile', methods=['GET', 'POST'])
def update_profile():
    if 'user' not in session:
        return redirect('/')
    avatar = session.get('avatar', 'images/avatar.png')
    name = session.get('name', '未登入')
    nickname = session.get('nickname', '未設定')

    if request.method == 'POST':
        new_name = request.form['name']
        new_nickname = request.form['nickname']


        conn = get_db_connection()
        cur = conn.cursor()

        # ✅ 更新使用者名稱+暱稱（使用 account 字串）
        cur.execute("UPDATE Users SET user_name = %s,nickname = %s WHERE account = %s", (new_name,new_nickname, session['user']))
        conn.commit()
        session['name'] = new_name
        session['nickname'] = new_nickname

        if 'photo' in request.files:
            file = request.files['photo']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filename = f"{session['user']}_{filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

                # ✅ 插入 images（user_id 改為 FK 整數）
                cur.execute("""
                    INSERT INTO images (file_name, file_path, user_id)
                    VALUES (%s, %s, %s)
                """, (filename, filepath, session['user_id']))
                conn.commit()

                session['avatar'] = filepath

        cur.close()
        conn.close()
        # flash('個人資料更新成功！')
        return redirect('/dashboard')

    return render_template('combine.html', avatar=avatar, name=name,nickname=nickname)

#頭像更新
@app.route('/upload_avatar', methods=['POST'])
def upload_avatar():
    if 'photo' not in request.files:
        flash('沒有選擇檔案')
        return redirect('/profile')

    photo = request.files['photo']
    if photo and allowed_file(photo.filename):
        filename = secure_filename(photo.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        photo.save(filepath)

        # 更新 session 中的 avatar 路徑
        session['avatar'] = filepath

        flash('頭像更新成功！')
        return redirect('/profile')
    else:
        flash('檔案格式不正確！')
        return redirect('/profile')
    

#聊天室
@app.route('/chat')
def chat():
    if 'user' in session:
        return render_template('chat.html', name=session['name'], avatar=session['avatar'])
    else:
        return redirect('/')

import requests
import json


if __name__ == '__main__':
    app.run(debug=True)
