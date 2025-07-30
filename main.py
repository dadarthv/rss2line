import requests
import os

LINE_TOKEN = os.getenv("LINE_TOKEN")
LINE_TO = os.getenv("LINE_TO")

def send_to_line(msg):
    headers = {"Authorization": f"Bearer {LINE_TOKEN}", "Content-Type": "application/json"}
    payload = {"to": LINE_TO, "messages": [{"type": "text", "text": msg}]}
    r = requests.post("https://api.line.me/v2/bot/message/push", headers=headers, json=payload)
    print(r.status_code, r.text)

def main():
    send_to_line("測試推播成功！")

if __name__ == "__main__":
    main()
