from flask import Flask, request, jsonify, render_template
import google.generativeai as genai
import mysql.connector
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Optional
from urllib.parse import urlparse

app = Flask(__name__)

# 設定 Gemini API 金鑰
genai.configure(api_key="AIzaSyBKl0pZ7wpCju8ZSTJLAX8ViJzldGlDxBs")

# 資料庫配置
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",  # 請確認您的 MySQL 密碼
    "database": "SA2",
    "port": 3309,  # XAMPP MySQL 端口
    "unix_socket": "/Applications/XAMPP/xamppfiles/var/mysql/mysql.sock"  # XAMPP MySQL socket 路徑
}

def get_db_connection():
    """獲取資料庫連接"""
    return mysql.connector.connect(**DB_CONFIG)

def is_url(text: str) -> bool:
    """檢查文字是否為有效的 URL"""
    try:
        result = urlparse(text)
        return all([result.scheme, result.netloc])
    except:
        return False

def get_gemini_response(context: str, question: str) -> str:
    """使用 Gemini 處理回應"""
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        chat = model.start_chat(history=[])
        response = chat.send_message(
            f"""你是一個幫助學生整理資訊的AI助理，需要調理清晰，並且根據學生輸入的關鍵字為：{question}，
            根據以下資料提供清楚明確的回答，並整理好排版：

{context}"""

        )
        return response.text.strip()
    except Exception as e:
        print(f"Gemini AI 錯誤：{str(e)}")
        return "抱歉，AI 處理過程中發生錯誤。"

def fetch_webpage_content(url: str) -> List[str]:
    """擷取網頁內容"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, timeout=10, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        contents = []
        
        # 移除不需要的標籤
        for tag in soup(['script', 'style', 'meta', 'link']):
            tag.decompose()
            
        # 獲取所有連結文字
        for link in soup.find_all('a'):
            href = link.get('href')
            text = link.get_text(strip=True)
            if href and text and len(text) > 5:  # 過濾太短的文字
                contents.append(text)
                
        return contents
    except:
        return []

def handle_keyword_question(question):
    """處理關鍵字問題"""
    conn = None
    cursor = None
    try:
        # 初始化數據庫連接
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # 檢查 FAQ 表中是否有答案
        cursor.execute("SELECT answer FROM faq WHERE question = %s", (question,))
        result = cursor.fetchone()
        if result:
            return result['answer']
        
        # 從 catched_content 表中搜索相關內容，使用更靈活的匹配方式
        cursor.execute("""
            SELECT content FROM catched_content 
            WHERE keyword LIKE %s 
            OR %s LIKE CONCAT('%%', keyword, '%%')
            OR keyword LIKE CONCAT('%%', %s, '%%')
            ORDER BY id DESC 
            LIMIT 1
        """, (f"%{question}%", question, question))
        result = cursor.fetchone()
        
        if not result:
            return "抱歉，我找不到相關的資訊。"
        
        # 使用 Gemini AI 生成摘要
        summary = get_gemini_response(result['content'], question)
        
        # 檢查 AI 回應是否有效
        if summary and not summary.startswith("抱歉"):
            # 只有在成功獲取 AI 回應時才記錄到資料庫
            cursor.execute("""
                INSERT INTO faq (question, answer) 
                VALUES (%s, %s)
            """, (question, summary))
            conn.commit()
        
        return summary
        
    except mysql.connector.Error as err:
        error_msg = f"資料庫錯誤：{err}"
        print(error_msg)
        return error_msg
    except Exception as e:
        error_msg = f"發生錯誤：{str(e)}"
        print(error_msg)
        return error_msg
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/')
def index():
    return render_template('chat.html')

@app.route('/ask', methods=['POST'])
def ask():
    try:
        data = request.get_json()
        if not data or "question" not in data:
            return jsonify({"error": "缺少必要參數"}), 400

        question = data["question"].strip()
        if not question:
            return jsonify({"error": "問題不能為空"}), 400

        response = handle_keyword_question(question)
        return jsonify({
            "response": f"問題：{question}\n回答：{response}",
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({"error": "系統處理請求時發生錯誤"}), 500

if __name__ == '__main__':
    app.run(debug=True)
