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
PROJECT_NAME = "Cyber Team Help - AI Security Core"

bot = Bot(token=TELEGRAM_BOT_TOKEN) if TELEGRAM_BOT_TOKEN else None

# Rotation of High-Tech & Cyber Security GIFs
CYBER_GIF_POOL = [
    "https://media.giphy.com/media/w4zX4PfkQmZ4xeG7ny/giphy.gif",
    "https://media.giphy.com/media/WWIvZaHUJEOWi5UhGV/giphy.gif",
    "https://media.giphy.com/media/xTiTnMhJTwNHChdTZS/giphy.gif"
]

# Thread-Safe Global System State
engine_state = {
    "running": True,
    "total_posts": 0,
    "last_topic": "অপেক্ষা করছে...",
    "last_error": None
}
state_lock = threading.Lock()

# Advanced Cyber Security & Ethical Hacking AI Knowledge Base (Bengali)
CYBER_AI_POSTS = [
    {
        "title": "অ্যাডভান্সড ফিশিং ডিফেন্স ও ইউআরএল অ্যানালিসিস",
        "content": "ফিশিং অ্যাটাক বর্তমানে এআই (AI) এবং ডিপফেক টেকনোলজি ব্যবহার করে আরও নিখুঁত করা হচ্ছে। ডোমেন স্পুফিং রোধে সবসময় SPF, DKIM এবং DMARC প্রোটোকল কনফিগারেশন চেক করুন। অচেনা লিংকে ক্লিক করার আগে স্যান্ডবক্স স্ক্যানার ব্যবহার করুন।",
        "tool": "VirusTotal / PhishTank Scanner",
        "link": "https://www.virustotal.com"
    },
    {
        "title": "ওয়েব অ্যাপ্লিকেশন সিকিউরিটি ও SQL ইনজেকশন প্রিভেনশন",
        "content": "ডেটাবেজ সিকিউরিটিতে প্যারামিটারাইজড কুয়েরি এবং প্রিপেয়ার্ড স্টেটমেন্ট ব্যবহার না করলে SQL Injection এর ঝুঁকি থাকে। ইথিকাল হ্যাকিং ও পেনিট্রেশন টেস্টার হিসেবে সবসময় ইনপুট স্যানিটাইজেশন নিশ্চিত করুন।",
        "tool": "OWASP ZAP / SQLmap (Educational)",
        "link": "https://www.zaproxy.org"
    },
    {
        "title": "পাসওয়ার্ড হাশ ক্র্যাকিং এবং ব্রুট-ফোর্স কাউন্টারমেজার",
        "content": "দুর্বল হাশ অ্যালগরিদম (যেমন MD5 বা SHA1 সল্ট ছাড়া) সহজেই ক্র্যাক করা সম্ভব। পাসওয়ার্ড সুরক্ষায় bcrypt বা Argon2 হ্যাকিং রেজিস্ট্যান্ট হ্যাশিং ব্যবহার করা বাধ্যতামূলক। রেইট লি লিমিটিং (Rate Limiting) ব্রুট-ফোর্স রোধ করে।",
        "tool": "Hashcat / John the Ripper",
        "link": "https://hashcat.net/hashcat/"
    },
    {
        "title": "ওপেন সোর্স ইন্টেলিজেন্স (OSINT) এবং ডিজিটাল ফুটপ্রিন্ট",
        "content": "ডিজিটাল সিকিউরিটি অডিটের জন্য OSINT অত্যন্ত শক্তিশালী মাধ্যম। পাবলিকলি উপলব্ধ মেটাডেটা, সোশ্যাল মিডিয়া ফুটপ্রিন্ট এবং ডোমেন রেকর্ড অ্যানালাইসিস করে সম্ভাব্য ভালনারেবিলিটি খুঁজে বের করা যায়।",
        "tool": "OSINT Framework & Sherlock",
        "link": "https://osintframework.com"
    },
    {
        "title": "নেটওয়ার্ক স্নাইপিং ও ওয়্যারশর্ক (Wireshark) এনালাইসিস",
        "content": "প্যাকেট অ্যানালাইসিসের মাধ্যমে নেটওয়ার্কের ভেতর দিয়ে যাওয়া ট্রাফিক মনিটর করা যায়। এনক্রিপটেড প্রোটোকল (যেমন HTTPS, TLS 1.3) ব্যবহার না করলে ডেটা প্লেইন টেক্সটে লিক হতে পারে।",
        "tool": "Wireshark Packet Analyzer",
        "link": "https://www.wireshark.org"
    },
    {
        "title": "সোশ্যাল ইঞ্জিনিয়ারিং এবং হিউম্যান ফায়ারওয়াল সচেতনতা",
        "content": "সিস্টেমের ফায়ারওয়াল যতই শক্তিশালী হোক না কেন, হিউম্যান এরর বা প্রলোভনের কারণে সিস্টেম ব্রেক হতে পারে। ফিশিং ইমেইল, ভয়েস স্পিয়ার ফিশিং এবং সামাজিক প্রলোভন থেকে বাঁচতে স্টাফদের নিয়মিত সাইবার সচেতনতা ট্রেনিং দিন।",
        "tool": "CISA Cyber Awareness Training",
        "link": "https://www.cisa.gov"
    }
];

# Professional Bengali Dark Web Dashboard HTML
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ project_name }} - AI Control Panel</title>
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
        <h1>🛡️ সাইবার টিম হেল্প (AI Bot)</h1>
        <div class="subtitle">ডেভেলপার: {{ developer }}</div>
        
        <div class="status-badge {{ 'running' if state.running else 'stopped' }}">
            {{ '🟢 এআই ম্যানেজমেন্ট বটের অবস্থা: সচল (প্রতি ২০ মিনিটে পোস্ট)' if state.running else '🔴 বটের অবস্থা: বন্ধ' }}
        </div>
        
        <div class="info-box">
            <div class="info-row"><span class="label">মোট এআই পোস্ট সংখ্যা:</span><span class="value">{{ state.total_posts }}</span></div>
            <div class="info-row"><span class="label">সর্বশেষ পোস্ট টপিক:</span><span class="value">{{ state.last_topic }}</span></div>
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
        
        <div class="footer">অটোমেটেড সাইবার সিকিউরিটি এডুকেশন ও ম্যানেজমেন্ট বট।</div>
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
            logger.info("AI Security bot engine started via Web Control Panel.")
        elif action == "stop":
            engine_state["running"] = False
            logger.info("AI Security bot engine stopped via Web Control Panel.")
    return redirect(url_for('home'))

def background_ai_security_bot_engine():
    global engine_state
    logger.info("AI Cyber Security 20-Min Auto-Posting Engine started.")
    
    while True:
        try:
            with state_lock:
                is_running = engine_state["running"]
                
            if not is_running:
                time.sleep(10)
                continue
                
            # Randomly select a cyber security topic and GIF
            post_item = random.choice(CYBER_AI_POSTS)
            selected_gif = random.choice(CYBER_GIF_POOL)
            
            # AI Management & Professional Formatted Post in Bengali
            post_message = (
                f"🛡️ <b>[CYBER TEAM HELP: AI INTELLIGENCE ADVISORY]</b> 🛡️\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🤖 <b>এআই সিকিউরিটি আপডেট ও এনালাইসিস</b>\n\n"
                f"📌 <b>মূল টপিক:</b> <code>{post_item['title']}</code>\n\n"
                f"💡 <b>এআই সিকিউরিটি ব্রিফিং:</b>\n{post_item['content']}\n\n"
                f"🛠️ <b>সরাসরি টুলস ও প্র্যাক্টিক্যাল রিসোর্স:</b>\n"
                f"• টুলস: <code>{post_item['tool']}</code>\n"
                f"• অফিশিয়াল লিংক: <a href='{post_item['link']}'>এখানে এক্সেস করুন</a>\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"⚙️ <b>বিশেষ সেবা ও প্রফেশনাল কাজের জন্য:</b>\n"
                f"যেকোনো ধরনের সাইবার সিকিউরিটি কনসালটেন্সি, সিকিউরিটি অডিট, ভালনারেবিলিটি এসেসমেন্ট বা কাস্টম প্রফেশনাল কাজের জন্য সরাসরি ইনবক্সে যোগাযোগ করুন: <b>{DEVELOPER_CREDIT}</b>\n\n"
                f"👥 <b>আমাদের অফিসিয়াল গ্রুপ:</b> <a href='{GROUP_LINK}'>Join Cyber Team Help</a>\n"
                f"👨‍💻 <b>Powered by AI Core & Developer:</b> <b>{DEVELOPER_CREDIT}</b>"
            )
            
            if bot and TELEGRAM_CHAT_ID:
                try:
                    async def send_ai_post():
                        await bot.send_animation(
                            chat_id=TELEGRAM_CHAT_ID, 
                            animation=selected_gif,
                            caption=post_message, 
                            parse_mode="HTML"
                        )
                    asyncio.run(send_ai_post())
                    
                    with state_lock:
                        engine_state["total_posts"] += 1
                        engine_state["last_topic"] = post_item['title']
                        engine_state["last_error"] = None
                        
                    logger.info(f"Successfully posted AI topic: {post_item['title']}")
                except TelegramError as te:
                    err_str = str(te)
                    logger.error(f"Telegram API Error: {err_str}")
                    with state_lock:
                        engine_state["last_error"] = f"Telegram Error: {err_str}"
            
            # প্রতি ২০ মিনিট (১২০০ সেকেন্ড) পর পর পরবর্তী পোস্ট আনলিমিটেড সাইকেলে চলতে থাকবে
            time.sleep(1200)
            
        except Exception as ex:
            err_str = str(ex)
            logger.error(f"Critical error in AI security bot engine: {err_str}")
            with state_lock:
                engine_state["last_error"] = err_str
            time.sleep(30)

# Start background engine on worker boot
if os.environ.get("WERKZEUG_RUN_MAIN") == "true" or os.environ.get("RENDER"):
    engine_thread = threading.Thread(target=background_ai_security_bot_engine, daemon=True)
    engine_thread.start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
