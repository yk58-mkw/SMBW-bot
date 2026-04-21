from flask import Flask
from threading import Thread
import os # ← これを追加

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run():
    # 8080 を 7860 に変更する
    port = int(os.environ.get("PORT", 7860))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()