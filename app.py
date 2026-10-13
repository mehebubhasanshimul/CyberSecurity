import os
import logging
import asyncio
import threading
import time
import random
from datetime import datetime, timezone
from flask import Flask, render_template_string, request, redirect, url_for
from telegram import Bot
from telegram.error import TelegramError
import requests

# Logging Setup
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Credentials & Constants
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "@shadow_joker_cyberteamhelp")
GROUP_LINK = "https://t.me/shadow_joker_cyberteamhelp"
DEVELOPER_CREDIT = "@SHADOW_JOKER_CTH"
PROJECT_NAME = "Cyber Team Help - Advanced AI Core"

bot = Bot(token=TELEGRAM_BOT_TOKEN) if TELEGRAM_BOT_TOKEN else None

# Pool of Cyber Security & Hacking GIFs
CYBER_GIF_POOL = [
    "https://media.giphy.com/media/w4zX4PfkQmZ4xeG7ny/giphy.gif",
    "https://media.giphy.com/media/WWIvZaHUJEOWi5UhGV/giphy.gif",
    "https://media.giphy.com/media/xTiTnMhJTwNHChdTZS/giphy.gif",
    "https://media.giphy.com/media/W23kW9Z07sQ3p7xS5j/giphy.gif"
]

# Thread-Safe Global System State
engine_state = {
    "running": True,
    "total_posts": 0,
    "last_topic": "অপেক্ষা করছে...",
    "last_error": None
}
state_lock = threading.Lock()

# Diverse Open-Source Cyber Security & Ethical Hacking Knowledge Base (Bengali)
CYBER_AI_POSTS = [
    {
        "title": "SQL Injection (SQLi) ও ডিফেন্সিভ কোডিং কৌশল",
        "content": "ওয়েব অ্যাপ্লিকেশনে ডেটাবেজ ইনপুট ভ্যালিডেশন সঠিকভাবে না থাকলে SQL Injection এর মাধ্যমে সম্পূর্ণ ডেটাবেজ কমপ্রোমাইজ হতে পারে। হ্যাকিং প্রতিরোধে সবসময় Prepared Statements এবং Parameterized Queries ব্যবহার করুন।",
        "tool": "OWASP ZAP / SQLmap (Educational Audit)",
        "link": "https://www.zaproxy.org"
    },
    {
        "title": "Nmap দিয়ে নেটওয়ার্ক পোর্ট স্ক্যানিং ও ভালনারেবিলিটি ডিটেকশন",
        "content": "নেটওয়ার্ক পেনিট্রেশন টেস্টারের জন্য Nmap হলো অন্যতম সেরা ওপেন-সোর্স টুল। এর মাধ্যমে টার্গেট সার্ভারে ওপেন পোর্ট, রানিং সার্ভিস এবং ওএস (OS) ভারsion ডিটেক্ট করে সম্ভাব্য লজিক্যাল ফ্লা গবেষণা করা যায়।",
        "tool": "Nmap Network Scanner",
        "link": "https://nmap.org"
    },
    {
        "title": "Cross-Site Scripting (XSS) এবং প্রিভেনশন মেথড",
        "content": "ম্যালিসিয়াস জাভাস্ক্রিপ্ট কোড ইউজারের ব্রাউজারে এক্সিকিউট করিয়ে কুকি বা সেশন টোকেন চুরি করার পদ্ধতি হলো XSS। আউটপুট এনকোডিং (Output Encoding) এবং Content Security Policy (CSP) হেডারের মাধ্যমে এটি ঠেকানো সম্ভব।",
        "tool": "PortSwigger Web Security Academy",
        "link": "https://portswigger.net/web-security"
    },
    {
        "title": "Wireshark দিয়ে প্যাকেট স্নাইফিং এবং ট্রাফিক অ্যানালাইসিস",
        "content": "নেটওয়ার্ক ট্রাফিকের রিয়েল-টাইম ক্যাপচার ও এনালাইসিসের জন্য Wireshark ব্যবহার করা হয়। সঠিক এনক্রিপশন (যেমন TLS 1.3) ছাড়া ডাটা ট্রান্সফার করলে স্নাইফার দিয়ে প্লেইনটেক্সট ক্রেডেনশিয়াল ক্যাপচার করা সম্ভব।",
        "tool": "Wireshark Packet Analyzer",
        "link": "https://www.wireshark.org"
    },
    {
        "title": "OSINT (Open Source Intelligence) এবং ডিজিটাল ফুটপ্রিন্টিং",
        "content": "টার্গেটের কোনো টেকনিক্যাল সিস্টেম সরাসরি হ্যাক না করে পাবলিকলি উপলব্ধ ইনফরমেশন (যেমন সোশ্যাল মিডিয়া, মেটাডেটা, সাব-ডোমেন রেকর্ড) সংগ্রহ করে সিকিউরিটি উইকনেস খুঁজে বের করাকেই OSINT বলে।",
        "tool": "OSINT Framework & Sherlock",
        "link": "https://osintframework.com"
    },
    {
        "title": "র্যানসমওয়্যার (Ransomware) এবং ডেটা ব্যাকআপ স্ট্র্যাটেজি",
        "content": "র্যানসমওয়্যার অ্যাটাকে সিস্টেমের ফাইল এনক্রিপ্ট করে হ্যাকাররা মুক্তিপণ দাবি করে। এই ধরণের ম্যালওয়্যার থেকে বাঁচতে নিয়মিত অফলাইন ব্যাকআপ (3-2-1 Backup Rule) মেইনটেইন করা সবচেয়ে বড় সিকিউরিটি ডিফেন্স।",
        "tool": "CISA Ransomware Guide",
        "link": "https://www.cisa.gov/stopransomware"
    },
    {
        "title": "ব্রুট-ফোর্স অ্যাটাক ও পাসওয়ার্ড হ্যাশিং (Bcrypt/Argon2)",
        "content": "দুর্বল হাশ অ্যালগরিদম যেমন MD5 বা SHA1 ব্যবহার করলে হ্যাকাররা সহজেই রেইনবো টেবিল বা ক্র্যাকিং টুল দিয়ে পাসওয়ার্ড বের করে ফেলে। সিস্টেমে সবসময় সল্টেড bcrypt বা Argon2 হ্যাশিং মেথড রাখা আবশ্যক।",
        "tool": "Hashcat Password Recovery",
        "link": "https://hashcat.net/hashcat/"
    },
    {
        "title": "সোশ্যাল ইঞ্জিনিয়ারিং এবং হিউম্যান ফায়ারওয়াল ডিফেন্স",
        "content": "প্রযুক্তির ফায়ারওয়াল যতই শক্তিশালী হোক না কেন, মানুষের অজ্ঞতা বা প্রলোভনকে কাজে লাগিয়ে সিস্টেম ব্রেক করা যায়। ফিশিং লিঙ্ক এবং ভয়েস স্পিয়ার ফিশিং সম্পর্কে সচেতনতা গড়ে তোলা অত্যন্ত জরুরি।",
        "tool": "Cyber Awareness Learning Hub",
        "link": "https://www.sans.org"
    }
];

# Smart Non-Repeating Post Queue Class
class NonRepeatingPostQueue:
    def __init__(self, posts):
        self.posts = posts
        self.queue = []
        self.refill()
        
    def refill(self):
        self.queue = list(self.posts)
        random.shuffle(self.queue)
        
    def get_next(self):
        if not self.queue:
            self.refill()
        return self.queue.pop(0)

post_manager = NonRepeatingPostQueue(CYBER_AI_POSTS)

# Professional Bengali Dark Web Dashboard HTML
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ project_name }} - Control Panel</title>
    <style>
        body { background-color: #0b0f19; color: #f1f5f9; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }
        .card { background: #1e293b; padding: 35px; border-radius: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.6); width: 100%; max-width: 480px; border: 1px solid #334155; }
        h1 { color: #38bdf8; font-size: 22px; margin-bottom: 5px; text-align: center; }
        .subtitle { text-align: center; color: #94a3b8; font-size: 13px; margin-bottom: 20px; }
        .status-badge { padding: 8px 16px; border-radius: 6px; font-weight: bold; display: block; text-align: center; margin-bottom: 20px; font-size: 13px; }
        .running { background-color: #065f46; color: #34d399; }
        .stopped { background-color: #7f1d1d; color: #fca5a5; }
        .info-box { background: #0f172a; padding: 15px; border-radius: 8px; font-size: 13px; margin-bottom: 20px; border: 1px solid #1e293b; }
        .info-row { display: flex; justify-content: space-between; margin-bottom: 8px; }
        .info-row:last-child { margin-bottom: 0; }
        .label { color: #94a3b8; }
        .value { color: #f8fafc; font-weight: 600; }
        .error-text { color: #f87171; font-size: 12px; margin-top: 10px; text-align: center; word-break: break-all; }
        .btn-group { display: flex; gap: 12px; }
        .btn { flex: 1; padding: 12px; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; text-decoration: none; text-align: center; font-size: 14px; transition: 0.2s; }
        .btn-start { background-color: #16a34a; color: white; }
        .btn-start:hover { background-color: #15803d; }
        .btn-stop { background-color: #dc2626; color: white; }
        .btn-stop:hover { background-color: #b91c1c; }
        .footer { margin-top: 20px; text-align: center; font-size: 11px; color: #64748b; }
        a { color: #38bdf8; text-decoration: none; }
    </style>
</head>
<body>
    <div class="card">
        <h1>🛡️ সাইবার টিম হেল্প (প্রো বট)</h1>
        <div class="subtitle">ডেভেলপার: {{ developer }}</div>
        
        <div class="status-badge {{ 'running' if state.running else 'stopped' }}">
            {{ '🟢 ইউনিক পোস্ট ইঞ্জিন: সচল (প্রতি ২০ মিনিটে নতুন পোস্ট)' if state.running else '🔴 বট বর্তমানে বন্ধ' }}
        </div>
        
        <div class="info-box">
            <div class="info-row"><span class="label">মোট প্রকাশিত পোস্ট:</span><span class="value">{{ state.total_posts }}</span></div>
            <div class="info-row"><span class="label">সর্বশেষ প্রকাশিত টপিক:</span><span class="value">{{ state.last_topic }}</span></div>
            <div class="info-row"><span class="label">টেলিগ্রাম গ্রুপ:</span><span class="value"><a href="{{ group_link }}" target="_blank">গ্রুপ ভিজিট করুন</a></span></div>
        </div>
        
        {% if state.last_error %}
        <div class="error-text">⚠️ ত্রুটি: {{ state.last_error }}</div>
        {% endif %}
        
        <form method="POST" action="/control" class="btn-group">
            <input type="hidden" name="action" value="{{ 'stop' if state.running else 'start' }}">
            <button type="submit" class="btn {{ 'btn-stop' if state.running else 'btn-start' }}">
                {{ 'বট বন্ধ করুন' if state.running else 'বট চালু করুন' }}
            </button>
        </form>
        
        <div class="footer">নন-রিপিটিং ওপেন সোর্স সাইবার সিকিউরিটি অটোমেশন সিস্টেম।</div>
    </div>
</body>
</html>
"""

@app.route("/")
def home():
    with state_lock:
        return render_template_string(
            HTML_TEMPLATE, 
            project_name=PROJECT_NAME, 
            developer=DEVELOPER_CREDIT, 
            group_link=GROUP_LINK,
            state=engine_state
        )

@app.route("/control", methods=["POST"])
def control():
    action = request.form.get("action")
    with state_lock:
        if action == "start":
            engine_state["running"] = True
            logger.info("Advanced Security bot started via Web Panel.")
        elif action == "stop":
            engine_state["running"] = False
            logger.info("Advanced Security bot stopped via Web Panel.")
    return redirect(url_for('home'))

def background_professional_security_engine():
    global engine_state
    logger.info("Professional Non-Repeating Cyber Security Engine started.")
    
    while True:
        try:
            with state_lock:
                is_running = engine_state["running"]
                
            if not is_running:
                time.sleep(10)
                continue
                
            # Get next unique post from the queue (No immediate repeats)
            post_item = post_manager.get_next()
            selected_gif = random.choice(CYBER_GIF_POOL)
            
            # Professional AI & Open-Source Formatted Post in Bengali
            post_message = (
                f"🛡️ <b>[CYBER TEAM HELP: ADVANCED SECURITY ADVISORY]</b> 🛡️\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🔥 <b>ওপেন-সোর্স সাইবার সিকিউরিটি আপডেট</b>\n\n"
                f"📌 <b>মূল বিষয়:</b> <code>{post_item['title']}</code>\n\n"
                f"💡 <b>প্রযুক্তিগত বিশ্লেষণ ও গাইডলাইন:</b>\n{post_item['content']}\n\n"
                f"🛠️ <b>প্র্যাক্টিক্যাল টুলস ও রিসোর্স লিংক:</b>\n"
                f"• টুলস/মডিউল: <code>{post_item['tool']}</code>\n"
                f"• অফিশিয়াল লিংক: <a href='{post_item['link']}'>এখানে এক্সেস করুন</a>\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"💼 <b>বিশেষ কাস্টম কনসালটেন্সি ও প্রফেশনাল সেবা:</b>\n"
                f"সিকিউরিটি অডিট, ভালনারেবিলিটি এসেসমেন্ট বা যেকোনো ধরনের কাস্টম সাইবার কাজের জন্য সরাসরি ইনবক্সে যোগাযোগ করুন: <b>{DEVELOPER_CREDIT}</b>\n\n"
                f"👥 <b>আমাদের অফিসিয়াল টেলিগ্রাম গ্রুপ:</b> <a href='{GROUP_LINK}'>Join Cyber Team Help</a>\n"
                f"👨‍💻 <b>Powered by AI & Developer Core:</b> <b>{DEVELOPER_CREDIT}</b>"
            )
            
            if bot and TELEGRAM_CHAT_ID:
                try:
                    async def send_pro_post():
                        await bot.send_animation(
                            chat_id=TELEGRAM_CHAT_ID, 
                            animation=selected_gif,
                            caption=post_message, 
                            parse_mode="HTML"
                        )
                    asyncio.run(send_pro_post())
                    
                    with state_lock:
                        engine_state["total_posts"] += 1
                        engine_state["last_topic"] = post_item['title']
                        engine_state["last_error"] = None
                        
                    logger.info(f"Successfully posted unique topic: {post_item['title']}")
                except TelegramError as te:
                    err_str = str(te)
                    logger.error(f"Telegram API Error: {err_str}")
                    with state_lock:
                        engine_state["last_error"] = f"Telegram Error: {err_str}"
            
            # নিখুঁতভাবে প্রতি ২০ মিনিট (১২০০ সেকেন্ড) পর পর পরবর্তী ইউনিক পোস্ট
            time.sleep(1200)
            
        except Exception as ex:
            err_str = str(ex)
            logger.error(f"Critical error in professional security engine: {err_str}")
            with state_lock:
                engine_state["last_error"] = err_str
            time.sleep(30)

# Start background engine on worker boot
if os.environ.get("WERKZEUG_RUN_MAIN") == "true" or os.environ.get("RENDER"):
    engine_thread = threading.Thread(target=background_professional_security_engine, daemon=True)
    engine_thread.start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
