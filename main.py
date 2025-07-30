import feedparser
import requests
from bs4 import BeautifulSoup
import openai
import os

# ===== 你的設定 =====
RSS_LIST = [
    "https://c3.coffee/category/%e5%92%96%e5%95%a1%e6%96%b0%e8%81%9e/feed/",
    "https://www.cupin.com.tw/blogs/cupin-blogs.atom"  # 這個網站是 Atom 格式
]
LINE_TOKEN = os.getenv("LINE_TOKEN")
LINE_TO = os.getenv("LINE_TO")
openai.api_key = os.getenv("OPENAI_API_KEY")
# ====================

def fetch_full_article(url):
    """ 抓取完整文章 HTML 並萃取正文 """
    try:
        res = requests.get(url, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        # 嘗試抓主要內容 (WordPress: .entry-content, Shopify/一般: article)
        article = soup.select_one('.entry-content') or soup.find('article')
        return article.get_text().strip() if article else soup.get_text()[:2000]
    except Exception as e:
        return f"文章抓取失敗: {e}"

def summarize_to_two_sentences(text):
    """ 用 GPT 生成 2 句話摘要 """
    prompt = f"請將以下文章內容整理為兩句話重點摘要，保留主要資訊：\n{text[:3000]}"
    try:
        resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"摘要失敗: {e}"

def send_to_line(msg):
    """ 推送訊息到 LINE """
    headers = {"Authorization": f"Bearer {LINE_TOKEN}", "Content-Type": "application/json"}
    payload = {"to": LINE_TO, "messages": [{"type": "text", "text": msg}]}
    r = requests.post("https://api.line.me/v2/bot/message/push", headers=headers, json=payload)
    print("LINE 回應：", r.status_code, r.text)

def main():
    for rss in RSS_LIST:
        feed = feedparser.parse(rss)
        for entry in feed.entries[:3]:  # 每個 RSS 抓最新 3 篇（可調整）
            full_text = fetch_full_article(entry.link)
            summary = summarize_to_two_sentences(full_text)
            message = f"【{entry.title}】\n{summary}\n\n連結：{entry.link}"
            send_to_line(message)

if __name__ == "__main__":
    main()
