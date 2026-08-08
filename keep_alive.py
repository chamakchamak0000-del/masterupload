import os
import logging
from flask import Flask
from threading import Thread

# Silence Flask's request logs — bot console stays clean
logging.getLogger("werkzeug").setLevel(logging.ERROR)

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive!", 200

@app.route('/health')
def health():
    return "OK", 200

def keep_alive():
    port = int(os.environ.get('PORT', 5000))
    t = Thread(
        target=lambda: app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False),
        daemon=True,
        name="keep-alive"
    )
    t.start()
    print(f"🌐 Keep-alive server started on port {port}")
