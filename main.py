import feedparser
import requests
from bs4 import BeautifulSoup
import openai
import os

# ============= 你的設定 =============
RSS_LIST = [
    "https://c3.coffee/category/%e5%92%96%e5%95%a1%e6%96%b0%e8%81%9e/feed/",
    "https://example1.com/feed/",
    "https://example2.com/feed/",
    "https://example3.com/feed/",
    "https://example4.com/feed/"
]
LINE_TOKEN = os.getenv("LINE_TOKEN")
LINE_TO = os.getenv("LINE_TO")
openai.api_key = os.getenv("OPENAI_API_KEY")
# ==================================

def fetch_full_article(url):
    """ 抓取完整文章 HTML 並萃取正文 """
    res = requests.get(url, timeout=10)
    soup = BeautifulSoup(res.text, 'html.parser')
    article = soup.select_one('.entry-content')  # WordPress 常見正文 class
    if not article:
        article = soup.find('article')
    return article.get_text().strip() if article else ""

def summarize_outline(text):
    """ 用 GPT 產出大綱 """
    prompt = f"請將以下文章整理成 3~5 點大綱：\n{text[:3000]}"
    resp = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role":"user","content":prompt}],
        temperature=0.3
    )
    return resp.choices[0].message.content.strip()

def send_to_line(msg):
    headers = {"Authorization": f"Bearer {LINE_TOKEN}", "Content-Type": "application/json"}
    payload = {"to": LINE_TO, "messages": [{"type": "text", "text": msg}]}
    requests.post("https://api.line.me/v2/bot/message/push", headers=headers, json=payload)

def main():
    for rss in RSS_LIST:
        feed = feedparser.parse(rss)
        if feed.entries:
            entry = feed.entries[0]  # 抓最新一篇
            full_text = fetch_full_article(entry.link)
            outline = summarize_outline(full_text)
            message = f"【{entry.title}】\n{outline}\n\n連結：{entry.link}"
            send_to_line(message)

if __name__ == "__main__":
    main()
