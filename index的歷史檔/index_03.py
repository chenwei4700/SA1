"""
這是一個基於 Flask 的聊天機器人應用，整合了以下功能：
1. Google Sheets 工左表1作為數據存儲，工作表2作為對話儲存
2. Gemini AI 作為對話引擎
3. 網頁爬蟲功能
4. 對話歷史記錄管理
"""

from flask import Flask, request, jsonify, render_template, session, flash, redirect, url_for
import google.generativeai as genai#Gemini AI

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
import mysql.connector
import os
from werkzeug.utils import secure_filename
from difflib import SequenceMatcher
from .post_02 import post_bp
from flask import Blueprint
import random
from flask_mail import Mail, Message#要pip
from flask_mail import Mail
from itsdangerous import URLSafeTimedSerializer
from .extention import mail, serializer
from flask import current_app



index_bp = Blueprint('index', __name__)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# 初始化 Flask 應用
   


index_bp.secret_key = 'your_secret_key_here'  # 用於加密 session 數據
index_bp.permanent_session_lifetime = timedelta(minutes=3)  # session 有效期為 3 分鐘
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
def get_db_connection():
    return mysql.connector.connect(
        user='root',
        password='',
        database='SA3',
        unix_socket='/Applications/XAMPP/xamppfiles/var/mysql/mysql.sock'
    )




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
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO temp_info (time, website_url, content) VALUES (%s, %s, %s)", (current_time, url, content[:1000]))
        conn.commit()
        cur.close()
        conn.close()          
    except Exception as e:
        logger.error(f"保存網頁內容時發生錯誤: {str(e)}")
        conn.rollback()

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
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT website_url, content FROM temp_info")
        all_values = cur.fetchall()#獲取所有行的內容
        cur.close()
        conn.close()
        
        # 确保有数据
        if not all_values or len(all_values) <= 1:
            return ""
        
    except Exception as e:
        logger.error(f"搜索暫存內容時發生錯誤: {str(e)}")
        return ""

def clear_cached_content():
    """
    清除暫存的網頁內容 - 更安全的方法
    """
    try:
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("Delete from temp_info")#刪除暫存表的所有內容
        conn.commit()#提交更改
        cur.close()
        conn.close()
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
        model = genai.GenerativeModel('gemini-2.0-flash')  # 使用正確的模型名稱
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT question FROM faq")
        fap_info = [row[0] for row in cur.fetchall()]
        cur.close()
        conn.close()
        # 首先判斷問題是否與資管系課業相關
        relevance_prompt = f"""
判斷以下問題是否與資管系(資訊管理系)的課業或資管學術內容相關：
問題："{question}"

請分析這個問題是否與以下資訊有關：


1.{fap_info}
2.若問題為某某老師或某某教授，則先以{fap_info}中有出現相關姓氏代表相關
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
4. 若問題為某某老師或某某教授，則先以姓氏當作其中一個關鍵詞

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


def is_similar(a, b, threshold=0.7):
    return SequenceMatcher(None, a, b).ratio() >= threshold

def collect_similar_answers_with_intent(question):
    try:
        # 先查詢暫存內容
        cached_content = search_cached_content(question)
        if cached_content:
            return cached_content, 0  # ⬅️ 回傳兩個值

        # 使用 Gemini 分析問題意圖
        intent_data = analyze_question_intent(question)
        print(f"問題意圖分析結果: {intent_data}")
        
        # 檢查問題是否與資管系課業相關
        if intent_data.get("is_relevant") == False:
            return "抱歉，我只能回答與資管系課業相關的問題。您的問題似乎與資管系課業無關。", 1  # ⬅️ 回傳兩個值

        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT * FROM faq")
            all_values = cur.fetchall()
            column_names = [desc[0] for desc in cur.description]
            cur.close()
            conn.close()
            if not all_values or len(all_values) < 2:
                return "抱歉，找不到相關回答。(FAQ表格為空)", 2  # ⬅️ 回傳兩個值

            question_col = -1
            answer_col = -1
            for i, col in enumerate(column_names):
                if "問題" in col or "question" in col.lower():
                    question_col = i
                elif "回答" in col or "answer" in col.lower():
                    answer_col = i

            if question_col == -1 or answer_col == -1:
                return "抱歉，無法辨識資料表中的問題或回答欄位。", 0  # ⬅️ 回傳兩個值

            data = []
            for row in all_values:
                question_text = row[question_col] if row[question_col] else ""
                answer_text = row[answer_col] if row[answer_col] else ""
                data.append({
                    "問題": question_text,
                    "回答": answer_text
                })
        except Exception as e:
            print(f"獲取FAQ數據時發生錯誤: {str(e)}")
            return "抱歉，系統查詢失敗。(獲取FAQ數據時出錯)", 0  # ⬅️ 回傳兩個值

        collected_responses = []

        search_terms = []
        for word in question.lower().split():
            if word and len(word) >= 2:
                search_terms.append(word)

        for keyword_data in intent_data.get("keywords", []):
            word = keyword_data.get("word")
            if word and isinstance(word, str):
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

        for row in data:
            question_text = row.get("問題", "").lower()
            matched = any(term in question_text or is_similar(term, question_text) for term in search_terms)

            if matched:
                answer = row.get("回答", "")
                if not answer:
                    continue
                words = answer.split()
                content_results = []

                for word in words:
                    if word and is_url(word):
                        content = fetch_webpage_content(word)
                        if content:
                            content_results.append(f"來自 {word} 的內容：\n{content}")

                full_response = f"問題：{row['問題']}\n回答：{answer}"
                if content_results:
                    full_response += "\n\n" + "\n\n".join(content_results)

                collected_responses.append(full_response)


        return "\n\n---\n\n".join(collected_responses),  {
                "unanswer_question": question,
                "created_at": datetime.now(),
                "number" : 2
            }
    except Exception as e:
        print(f"收集答案時發生錯誤: {str(e)}")
        return f"抱歉，系統查詢失敗。錯誤信息: {str(e)}", 0  # ⬅️ 也補上第二個值

# 修改 Gemini 回應函數
def get_gemini_response(context, question):
    """
    使用 Gemini 生成回答
    
    """
    try:
        # 檢查是否已經判斷為不相關的問題
        if "抱歉，我只能回答與資管系課業相關的問題" in context:
            return context
            
        model = genai.GenerativeModel('gemini-2.0-flash')  # 使用正確的模型名稱
        
        prompt = f"""
你是一個專業的資管系教育助理。
使用者的原始問題是：「{question}」

請嚴格根據以下提供的「相關資料」，專門針對使用者的「原始問題」：「{question}」提供一個完整且具體的回答。
你的主要任務是回答「{question}」。請利用「相關資料」中的資訊來輔助你的回答，但不要偏離「{question}」的主旨。
如果「相關資料」中包含了看起來像問題的文本，請僅將它們視為背景信息，除非它們直接解答「{question}」。
不要自己生成新的問題，或主要回答「相關資料」中的問題。

以下是相關資料：
---
{context}
---

請確保回答：
1. 直接回應「{question}」的重點。
2. 條理分明。
3. 如果有相關的網頁資訊，請整合進回答中，所有連結請使用 HTML 格式超連結（<a href="..." target="_blank">網站名稱</a>），點擊後可在新分頁開啟。
4. 如果問題與資管系課業無關，或「相關資料」不足以回答「{question}」，請委婉拒絕並說明，以很抱歉開頭。
"""
        
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        logger.error(f"生成 Gemini 回答時發生錯誤: {str(e)}", exc_info=True)
        return "抱歉，我現在無法處理您的請求。請稍後再試。"



@index_bp.route('/chatroom')
def chatroom():
    """
    渲染聊天頁面
    
    """
    avatar = session.get('avatar', 'images/avatar.png')
    name = session.get('name', '未登入')
    id = session.get('user_id')

    return render_template('chat.html',
                            avatar=avatar,
                            name=name,
                            id=id)

@index_bp.route('/ask', methods=['POST'])
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
        collected_info, unanswer_data = collect_similar_answers_with_intent(question)
        logger.debug(f"收集到的信息：{collected_info[:100]}...")
        logger.debug(f"Unanswer data: {unanswer_data}") # Good to log this for debugging

        # Initialize final_answer
        final_answer = ""

        # Flag to indicate if Gemini should be called
        should_call_gemini = True

        
        if should_call_gemini:
            logger.debug(f"將收集到的信息交給 Gemini 整理：{collected_info[:100]}...")
            final_answer = get_gemini_response(collected_info, question)
            if final_answer.startswith("很抱歉"):
                # If Gemini fails, we can still use the collected information
                try:
                    conn = get_db_connection()
                    cur = conn.cursor()
                    cur.execute("""
                    INSERT INTO unanswer (unanswer_q)
                    VALUES (%s)
                    """, (
                        unanswer_data["unanswer_question"],
                    ))
                    conn.commit()
                    cur.close()
                    conn.close()
                    logger.info("已記錄無法回答的問題至 unanswer 表")
                except Exception as db_err:
                    logger.error(f"記錄 unanswer 資料表時出錯: {db_err}", exc_info=True)
                    logger.debug(f"Gemini 回應失敗，使用收集到的信息：{final_answer[:100]}...")
                else:
                    logger.debug(f"Gemini 整理後答案：{final_answer[:100]}...")
        # If final_answer is still empty here (shouldn't happen if logic is correct, but as a fallback)
        elif not final_answer:
            logger.warning("Final answer was not set, and Gemini was not called. Defaulting to a generic error.")
            final_answer = "抱歉，系統處理時遇到未預期的情況，無法提供回答。"

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
@index_bp.route('/clear_history', methods=['POST'])
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
    
@index_bp.route("/feedback", methods=["POST"])
def feedback():
    data = request.get_json()
    question = data.get("question")
    answer = data.get("answer")
    solved = data.get("solved")
    suggestion = data.get("suggestion")
    try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("INSERT INTO feedback(time, question, answer, suggest, solved ) VALUES (%s, %s, %s, %s, %s)", (datetime.now(), question, answer, suggestion, solved))
            conn.commit()
            cur.close()
            conn.close()
            print("回饋資料已儲存")
    except Exception as e:
            print(f"儲存進資料庫時發生錯誤: {str(e)}")
            
    
    return jsonify({"message": "回饋已收到"}), 200



# ✅ 註冊交流區 blueprint
index_bp.register_blueprint(post_bp, url_prefix='/post')

# ✅ MySQL 資料庫連線



# ✅ 上傳檔案設定
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'heic'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ✅ 首頁（登入頁）
@index_bp.route('/')
def home():
    return render_template('login.html')

@index_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        account = request.form['account']
        password = request.form['password']

        conn = get_db_connection()
        cur = conn.cursor()

        # 查詢使用者資料
        cur.execute("SELECT * FROM Users WHERE account = %s", (account,))
        user = cur.fetchone()

        if not user:
            flash('帳號不存在')
        elif user[2] != password:
            flash('密碼錯誤')
        elif user[5] != 1:
            flash('尚未完成信箱驗證')
        else:
            session['user'] = user[1]
            session['user_id'] = user[0]
            session['name'] = user[3]
            session['role'] = user[4]

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

    return render_template('login.html')


# ✅ 登出
@index_bp.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# ✅ 主頁（dashboard）
@index_bp.route('/dashboard')
def dashboard():
    if 'user' in session:
        return render_template('main.html', name=session['name'], avatar=session['avatar'])
    else:
        return redirect('/')

# ✅ 註冊新帳號
@index_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        account = request.form['account']
        password = request.form['password'] # 原密碼，建議雜湊處理
        name = request.form['name']
        nickname = request.form.get('nickname', '') # 獲取暱稱，若無則為空字串

        # --- 密碼雜湊 (建議實施) ---
        # from werkzeug.security import generate_password_hash
        # hashed_password = generate_password_hash(password)

        # --- 基本驗證 ---
        if not re.match(r'^\d{9}@m365\.fju\.edu\.tw$', account):
            flash('請使用 9 碼學號 + @m365.fju.edu.tw 註冊')
            return redirect(url_for('index.register'))
        if len(password) < 6:
            flash('密碼至少 6 碼')
            return redirect(url_for('index.register'))
        if not name: # 簡單檢查姓名是否為空
            flash('使用者姓名不能為空')
            return redirect(url_for('index.register'))

        conn = None
        cur = None
        try:
            conn = get_db_connection()
            cur = conn.cursor()

            cur.execute("SELECT * FROM Users WHERE account = %s", (account,))
            if cur.fetchone():
                flash('帳號已存在')
                return redirect(url_for('index.register'))

            # --- 插入使用者資料 (包含暱稱) ---
            # 假設 Users 表有 user_id (SERIAL PRIMARY KEY), account, password, user_name, nickname, role, is_verified
            # 注意：此處 password 仍為原始密碼，應替換為 hashed_password
            sql_insert_user = """
                INSERT INTO Users (account, password, user_name, nickname, role, is_verified) 
                VALUES (%s, %s, %s, %s, 'U', 0) 
            """ # RETURNING user_id 是 PostgreSQL 的語法，MySQL/SQLite 有其他方式獲取 lastrowid
            cur.execute(sql_insert_user, (account, password, name, nickname)) # 使用 password, 不是 hashed_password
            user_id = cur.lastrowid # 獲取新註冊使用者的 user_id

            # --- 處理頭像上傳 ---
            if 'photo' in request.files:
                file = request.files['photo']
                if file and file.filename != '' and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    # 為了避免檔名衝突，可以加上 user_id 或 account (確保 account 字元適合檔名)
                    # unique_filename = f"{user_id}_{filename}" # 或 f"{account.split('@')[0]}_{filename}"
                    unique_filename = f"{user_id}_{filename}"
                    
                    # 確保 UPLOAD_FOLDER 路徑是絕對的或相對於正確的基準點
                    upload_folder = current_app.config['UPLOAD_FOLDER'] 
                    # upload_folder = index_bp.config['UPLOAD_FOLDER']
                    os.makedirs(upload_folder, exist_ok=True) # 確保上傳目錄存在
                    filepath = os.path.join(upload_folder, unique_filename)
                    
                    file.save(filepath)

                    # 將頭像資訊存入 images 資料表
                    cur.execute("""
                        INSERT INTO images (file_name, file_path, user_id)
                        VALUES (%s, %s, %s)
                    """, (unique_filename, filepath, user_id))
                elif file and file.filename != '': # 如果上傳了檔案但不符合類型
                    flash('上傳的頭像檔案類型不被允許。')
                    # 決定是否因為頭像錯誤而中止註冊，或僅提示並繼續（不保存頭像）
                    # 此處選擇繼續註冊，不保存不合規的頭像

            conn.commit() # 所有資料庫操作成功後才提交

            # --- 寄送驗證信 (與原程式碼相同) ---
            token = serializer.dumps(account, salt='email-confirm')
            verify_url = url_for('index.verify_email', token=token, _external=True)
            
            # 假設 index_bp.config['MAIL_USERNAME'] 已被正確設定，或使用 current_app.config
            sender_email = current_app.config.get('MAIL_USERNAME', 'default_sender@example.com')

            msg = Message(subject="Email Verification",
                          sender=sender_email, # 使用 config 中的寄件者
                          recipients=[account])
            msg.body = f"""您好，

感謝您註冊本平台！
請點擊以下連結完成帳號驗證：

{verify_url}

此連結一小時內有效，請盡快點擊。

祝您使用愉快！
"""
            mail.send(msg)
            
            flash('註冊成功！請至信箱收驗證信完成啟用')
            return redirect(url_for('index.login'))

        except Exception as e:
            if conn:
                conn.rollback() # 如果發生錯誤，回滾資料庫操作
            flash(f'註冊過程中發生錯誤：{e}')
            # 可以記錄更詳細的錯誤到日誌 current_app.logger.error(f"Registration error: {e}")
            return redirect(url_for('index.register'))
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    return render_template('register.html') # GET 請求時

# ✅ 驗證連結
@index_bp.route('/verify/<token>')
def verify_email(token):
    try:
        email = serializer.loads(token, salt='email-confirm', max_age=3600)
    except:
        flash('連結已失效或錯誤')
        return redirect('/login')

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE Users SET is_verified = 1 WHERE account = %s", (email,))
    conn.commit()
    cur.close()
    conn.close()
    flash('驗證成功！請登入')
    return redirect('/login')

# ✅ 修改名字＋上傳頭像（合併版）
@index_bp.route('/update_profile', methods=['GET', 'POST'])
def update_profile():
    if 'user' not in session:
        return redirect('/')
    avatar = session.get('avatar', 'images/avatar.png')
    name = session.get('name', '未登入')

    if request.method == 'POST':
        new_name = request.form['name']

        conn = get_db_connection()
        cur = conn.cursor()

        # ✅ 更新使用者名稱（使用 account 字串）
        cur.execute("UPDATE Users SET user_name = %s WHERE account = %s", (new_name, session['user']))
        conn.commit()
        session['name'] = new_name

        if 'photo' in request.files:
            file = request.files['photo']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filename = f"{session['user']}_{filename}"
                filepath = os.path.join(index_bp.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)

                # ✅ 插入 images（user_id 改為 FK 整數）
                cur.execute("""
                    INSERT INTO images (file_name, file_path, uploadtime, user_id)
                    VALUES (%s, %s, NOW(), %s)
                """, (filename, filepath, session['user_id']))
                conn.commit()

                session['avatar'] = filepath

        cur.close()
        conn.close()
        # flash('個人資料更新成功！')
        return redirect('/dashboard')

    return render_template('combine.html', avatar=avatar, name=name)


    
def get_recent_announcements():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        time_threshold = datetime.now() - timedelta(days=3)  # 過去三天
        cursor.execute("""
            SELECT * FROM Announcements 
            WHERE created_at >= %s 
              AND content IS NOT NULL 
              AND content != '' 
            ORDER BY created_at DESC
        """, (time_threshold,))
        
        announcements = cursor.fetchall()
        
        cursor.close()
        conn.close()
        return announcements if announcements else []
    except Exception as e:
        print(f"Error fetching announcements: {e}")
        return []
    






#這裡下面是公告部分
@index_bp.route('/announcements')
def view_all_announcements():
    if 'user' not in session:
        return redirect('/')
        
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT * FROM Announcements
            WHERE content IS NOT NULL AND content != ''
            ORDER BY created_at DESC
        """)

        all_announcements = cursor.fetchall()
        cursor.close()
        conn.close()
    
        avatar = session.get('avatar', 'images/avatar.png')
        name = session.get('name', '未登入')
        id = session.get('user_id')

        return render_template('announcements.html',
                            announcements=all_announcements,
                            avatar=avatar,
                            name=name,
                            id=id)
    except Exception as e:
        flash("無法載入公告")
        return render_template('announcements.html', announcements=[])
    
@index_bp.route('/announcement/edit/<int:id>', methods=['PUT'])
def edit_announcement(id):
    if session.get('role') != 'M':
        return jsonify({'message': '權限不足'}), 403

    data = request.get_json()
    title = data.get('title')
    content = data.get('content')

    if not title or not content:
        return jsonify({'message': '標題和內容皆不得為空'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE announcements SET title = %s, content = %s WHERE id = %s",
        (title, content, id)
    )
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'message': '公告已更新'})


@index_bp.route('/announcement/delete/<int:id>', methods=['DELETE'])
def delete_announcement(id):
    if session.get('role') != 'M':
        return jsonify({'message': '權限不足'}), 403

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM announcements WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'message': '公告已刪除'})



@index_bp.route('/announcement/add', methods=['POST'])
def add_announcement():
    if session.get('role') != 'M':
        return jsonify({'message': '權限不足'}), 403

    data = request.get_json()
    title = data.get('title')
    content = data.get('content')

    if not title or not content:
        return jsonify({'message': '標題與內容皆為必填'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Announcements (title, content, created_at) VALUES (%s, %s, NOW())",
        (title, content)
    )
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'message': '公告已成功發布'})

@index_bp.route("/random_questions")
def random_questions():
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT question FROM faq")
    all_questions = [q[0] for q in cursor.fetchall()]
    cursor.close()
    conn.close()

    random.shuffle(all_questions)
    return jsonify(all_questions[:4])

@index_bp.route('/upload_avatar', methods=['POST'])
def upload_avatar():
    if 'photo' not in request.files:
        flash('沒有選擇檔案')
        return redirect('/profile')

    photo = request.files['photo']
    if photo and allowed_file(photo.filename):
        filename = secure_filename(photo.filename)
        filepath = os.path.join(index_bp.config['UPLOAD_FOLDER'], filename)
        photo.save(filepath)

        # 更新 session 中的 avatar 路徑
        session['avatar'] = filepath

        flash('頭像更新成功！')
        return redirect('/profile')
    else:
        flash('檔案格式不正確！')
        return redirect('/profile')
    




