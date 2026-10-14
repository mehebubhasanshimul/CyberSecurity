import os
import html
import time
import random
import logging
import threading
import requests

from datetime import datetime, timezone, timedelta
from flask import Flask, render_template_string, request, redirect, url_for

# =========================================================
# CYBER TEAM HELP - ADVANCED KNOWLEDGE CORE BOT
# Single file: app.py
# =========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
CHAT_ID = os.getenv(
    "TELEGRAM_CHAT_ID",
    "@shadow_joker_cyberteamhelp"
).strip()

GROUP_LINK = "https://t.me/shadow_joker_cyberteamhelp"
PRIVATE_GROUP_LINK = "https://t.me/+DLEo8TQ1PjIzYzFl"
DEVELOPER = "@SHADOW_JOKER_CTH"
PROJECT_NAME = "CYBER TEAM HELP | Advanced Knowledge Core"

POST_INTERVAL = max(
    60, int(os.getenv("POST_INTERVAL", "1200"))
)

REQUEST_TIMEOUT = 25

CYBER_GIFS = [
    "https://media.giphy.com/media/TFPdmm3rdzeZ0kP3zG/giphy.gif",
    "https://media.giphy.com/media/lMwHQ7201A72B6JqOW/giphy.gif",
    "https://media.giphy.com/media/WfkmFXSjRYbDjtohJj/giphy.gif",
    "https://media.giphy.com/media/26FPKhUtNG3TW74f6/giphy.gif",
    "https://media.giphy.com/media/IXnygGeB6LPPi/giphy.gif",
    "https://media.giphy.com/media/VGwTq3G6a39cI/giphy.gif",
    "https://media.giphy.com/media/RDZo7znAdn2u7sAcWH/giphy.gif",
    "https://media.giphy.com/media/2i7jspnRBYgg6v4Oki/giphy.gif",
    "https://media.giphy.com/media/6NjTciHDVFh11crDfY/giphy.gif",
    "https://media.giphy.com/media/qQgKLMJvWEZKI2Hfvo/giphy.gif",
]

# =========================================================
# BRAND NEW KNOWLEDGE BASE & TOOLS (NO OLD POSTS)
# =========================================================

POSTS = [
    {
        "category": "🛡️ CTH EXCLUSIVE HUB",
        "title": "Cyber Team Help All-in-One Web Dashboard",
        "content": (
            "আমাদের নিজস্ব তৈরি সম্পূর্ণ অল-ইন-ওয়ান সাইবার টুলস এবং "
            "ইউটিলিটি ড্যাশবোর্ড থেকে প্রয়োজনীয় সেবা এক ক্লিকেই ব্যবহার করুন।\n\n"
            "✅ এডভান্সড ইউটিলিটি ও অ্যানালিটিক্স টুলস।\n"
            "✅ সম্পূর্ণ ডার্ক ও সাইবারস্পেস ইন্টারফেস।\n"
            "✅ ফাস্ট রেসপন্স ও নিয়মিত ফিচার আপডেট।"
        ),
        "tool": "CTH All-in-One Hub Portal",
        "link": "https://cyber-team-help-all-in-one.vercel.app/",
        "safety": "অনুমোদিত ও বৈধ কাজের জন্য টুলস ব্যবহার করুন।"
    },
    {
        "category": "🔐 ACCOUNT RECOVERY",
        "title": "Facebook Disabled & Identity Verification Fix 2026",
        "content": (
            "আপনার ফেসবুক অ্যাকাউন্ট ডিসেবল বা লক হলে নিচের এডভান্সড গাইড ফলো করুন:\n\n"
            "১. ব্রাউজার প্রাইভেট মোড/ছদ্মবেশী ট্যাব থেকে ফেসবুক আইডি লগইন করুন।\n"
            "২. 'Request Review' পেজে সঠিক NID/Passport-এর উভয় পিঠের স্পষ্ট ছবি দিন।\n"
            "৩. ফেসবুক সিকিউরিটি টিমের নোটিফিকেশন পর্যন্ত ধৈর্য্য ধরে অপেক্ষা করুন।\n"
            "৪. কোনো ভুয়া রিকভারি এজেন্টকে টাকা বা পাসওয়ার্ড দিয়ে প্রতারিত হবেন না।"
        ),
        "tool": "Facebook Official Help Center",
        "link": "https://www.facebook.com/help/",
        "safety": "শুধুমাত্র নিজের অর্জিনাল অ্যাকাউন্টে ব্যবহার করুন।"
    },
    {
        "category": "⚡ CTH UTILITY TOOLS",
        "title": "Unlimited Text & Data Generator Web Tool",
        "content": (
            "ডেভেলপিং, স্ক্রিপ্টিং ও টেস্ট ডাটা ফিল করার জন্য আনলিমিটেড "
            "টেক্সট ও ফরম্যাটিং দরকার হলে আমাদের এই টুলটি ট্রাই করুন।\n\n"
            "• সুপারফাস্ট কাস্টম টেক্সট জেনারেশন।\n"
            "• কোনো প্রকার পেজ রিলোড ছাড়াই ইনস্ট্যান্ট আউটপুট।"
        ),
        "tool": "Unlimited Text Generator Tool",
        "link": "https://unlimited-text-generator-cth-2esh.vercel.app/",
        "safety": "ডেভেলপমেন্ট ও এডিটিং পারপাসে ব্যবহারযোগ্য।"
    },
    {
        "category": "🔐 ACCOUNT RECOVERY",
        "title": "Instagram Suspended & Appeal Review Complete Guide",
        "content": (
            "ইনস্টাগ্রাম অ্যাকাউন্ট সাসপেন্ড হলে রিকভার করার সঠিক পদ্ধতি:\n\n"
            "✅ অফিশিয়াল ইনস্টাগ্রাম অ্যাপ দিয়ে ইউজারনেম ও পাসওয়ার্ড দিয়ে ঢুকুন।\n"
            "✅ স্ক্রিনে 'Appeal' অপশন আসলে আপনার অ্যাক্টিভ ইমেইল ও ফোন নম্বর দিন।\n"
            "✅ সেলফি কোড (Handheld Selfie Code) চাইলে স্পষ্ট ও পরিষ্কার ছবি আপলোড করুন।\n"
            "❌ কোনো আনঅফিশিয়াল এপিআই বা বট অ্যাপ দিয়ে লগইন করবেন না।"
        ),
        "tool": "Instagram Help Center Portal",
        "link": "https://help.instagram.com/",
        "safety": "অফিশিয়াল অ্যাপ বা হেল্প সেন্টার ব্যবহার করা নিরাপদ।"
    },
    {
        "category": "🛠️ SECURITY & ID TOOLS",
        "title": "Link & ID Security Management Utilities",
        "content": (
            "আপনার সোশ্যাল মিডিয়া লিংক ও অ্যাকাউন্ট সিকিউরিটি চেক করতে "
            "আমাদের এই নতুন ইউটিলিটি টুলসের সাহায্য নিতে পারেন।\n\n"
            "🔍 লিংক অ্যানালাইসিস ও সেফটি চেকিং এক ক্লিকেই সম্পূর্ণ করুন।"
        ),
        "tool": "CTH Security Utility Tools",
        "link": "https://link-to-id-hack-tolls-cth.vercel.app/",
        "safety": "নিজের একাউন্ট সেফটি ও চেকিংয়ের জন্য ব্যবহার করুন।"
    },
    {
        "category": "🔐 ACCOUNT SECURITY",
        "title": "Facebook / Instagram Hacked Account Recovery Roadmap",
        "content": (
            "যদি আপনার একাউন্টের ইমেইল বা পাসওয়ার্ড হ্যাকার পরিবর্তন করে ফেলে:\n\n"
            "১. অনতিবিলম্বে Meta Secured Recovery Portal-এ প্রবেশ করুন।\n"
            "২. 'My account is compromised' সিলেক্ট করে আগের ডিভাইস দিয়ে চেষ্টা করুন।\n"
            "৩. প্রাইমারি ইমেইল রিকভার করে আগের বিশ্বস্ত ব্রাউজার থেকে আপিল জমা দিন।\n"
            "৪. টু-ফ্যাক্টর অথেন্টিকেশন (2FA Authenticator App) অন রাখুন।"
        ),
        "tool": "Meta Security Hacked Help Portal",
        "link": "https://www.facebook.com/hacked",
        "safety": "কারো সাথে টু-ফ্যাক্টর ব্যাকআপ কোড শেয়ার করবেন না।"
    },
    {
        "category": "💻 ETHICAL HACKING",
        "title": "Web Application Penetration Testing Roadmap",
        "content": (
            "ওয়েব সিকিউরিটি ও পেনেট্রেশন টেস্টিং শেখার সঠিক নিয়মাবলী:\n\n"
            "📌 Step 1: HTTP/HTTPS রিকোয়েস্ট ও রেসপন্স অ্যানালাইসিস।\n"
            "📌 Step 2: Burp Suite দিয়ে ট্রাফিক ইন্টারসেপ্ট ও টেস্টিং।\n"
            "📌 Step 3: OWASP Top 10 বাগস (SQLi, XSS, CSRF, IDOR)।\n"
            "📌 Step 4: লিগ্যাল বাউন্টি প্ল্যাটফর্মে (HackerOne/Bugcrowd) প্র্যাকটিস।"
        ),
        "tool": "PortSwigger Web Security Academy",
        "link": "https://portswigger.net/web-security",
        "safety": "অনুমতি ছাড়া কোনো ওয়েবসাইট বা সার্ভারে অ্যাটাক দেওয়া নিষিদ্ধ।"
    },
    {
        "category": "🐍 PYTHON SECURITY",
        "title": "Python Cyber Automation & Threat Scanning",
        "content": (
            "পাইথন দিয়ে ডিফেন্সিভ সাইবার সিকিউরিটি ও অটোমেশন টুলস তৈরি শিখুন:\n\n"
            "• Python Requests & BeautifulSoup দিয়ে ডেটা স্ক্র্যাপিং।\n"
            "• Socket প্রোগামিং দিয়ে পোর্ট ও সার্ভিস চেকিং।\n"
            "• Telegram Bot API দিয়ে রিয়েল-টাইম সিকিউরিটি অ্যালার্ট।"
        ),
        "tool": "Python Official Standard Documentation",
        "link": "https://docs.python.org/3/tutorial/",
        "safety": "নিজের সোর্স কোডে এপিআই কি প্রকাশ করবেন না।"
    }
]

# =========================================================
# THREAD-SAFE STATE AND NON-REPEATING QUEUE
# =========================================================

state_lock = threading.RLock()

engine_state = {
    "running": True,
    "total_posts": 0,
    "last_topic": "অপেক্ষা করছে...",
    "last_post_time": "এখনো পোস্ট হয়নি",
    "last_error": None,
    "next_post_in": POST_INTERVAL,
    "status": "Starting"
}


class NonRepeatingPostQueue:
    def __init__(self, items):
        self.items = list(items)
        self.queue = []
        self.lock = threading.Lock()
        self.last_item = None
        self._refill()

    def _refill(self):
        self.queue = self.items[:]
        random.shuffle(self.queue)

        if (
            len(self.queue) > 1
            and self.last_item is not None
            and self.queue[-1]["title"] == self.last_item
        ):
            self.queue[0], self.queue[-1] = (
                self.queue[-1], self.queue[0]
            )

    def get_next(self):
        with self.lock:
            if not self.queue:
                self._refill()

            item = self.queue.pop()
            self.last_item = item["title"]
            return item


post_queue = NonRepeatingPostQueue(POSTS)

# =========================================================
# TELEGRAM API
# =========================================================

def telegram_api(method, payload):
    if not BOT_TOKEN:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN Environment Variable সেট করা নেই।"
        )

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"

    response = requests.post(
        url,
        json=payload,
        timeout=REQUEST_TIMEOUT
    )
    response.raise_for_status()

    result = response.json()

    if not result.get("ok"):
        raise RuntimeError(result.get("description", "Telegram API error"))

    return result


def send_telegram_post(item):
    """
    Send one professional animated GIF and then the complete formatted post per message.
    """

    title = html.escape(item["title"])
    category = html.escape(item["category"])
    content = html.escape(item["content"])
    tool = html.escape(item["tool"])
    link = html.escape(item["link"], quote=True)
    safety = html.escape(item["safety"])
    developer = html.escape(DEVELOPER)
    group_link = html.escape(GROUP_LINK, quote=True)
    private_group = html.escape(PRIVATE_GROUP_LINK, quote=True)

    now = datetime.now(
        timezone(timedelta(hours=6))
    ).strftime("%d-%m-%Y | %I:%M %p")

    message = (
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🛡️ <b>CYBER TEAM HELP</b>\n"
        "⚡ <b>ADVANCED KNOWLEDGE & SECURITY HUB</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{category}\n\n"
        f"📌 <b>{title}</b>\n\n"
        f"📚 <b>বিস্তারিত গাইড:</b>\n"
        f"{content}\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🧰 <b>রিসোর্স ও শেখার লিংক</b>\n"
        f"🔗 <a href=\"{link}\">{tool}</a>\n\n"
        "⚠️ <b>নিরাপত্তা নোট:</b>\n"
        f"{safety}\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"🕒 <b>প্রকাশের সময়:</b> {now}\n"
        f"👨‍💻 <b>Developer:</b> {developer}\n"
        f"👥 <a href=\"{group_link}\">JOIN PUBLIC GROUP</a>\n"
        f"🔒 <a href=\"{private_group}\">JOIN PRIVATE VIP GROUP</a>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"💬 <b>কাজের জন্য ইনবক্সে মেসেজ দিন: {developer}</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "💡 <i>শিখুন • নিরাপদ থাকুন • দায়িত্বশীল হোন</i>"
    )

    gif_sent = False
    if CYBER_GIFS:
        selected_gif = random.choice(CYBER_GIFS)

        try:
            telegram_api("sendAnimation", {
                "chat_id": CHAT_ID,
                "animation": selected_gif,
                "caption": (
                    "🛡️ <b>CYBER TEAM HELP</b>\n"
                    "📚 Cybersecurity • Tools • Privacy\n"
                    f"👨‍💻 {developer}"
                ),
                "parse_mode": "HTML"
            })
            gif_sent = True

        except Exception as exc:
            logger.warning("GIF delivery failed: %s", exc)

    telegram_api("sendMessage", {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    })

    return gif_sent


# =========================================================
# PROFESSIONAL BACKGROUND ENGINE
# =========================================================

def background_professional_security_engine():
    logger.info("Cyber Team Help engine started.")

    while True:
        with state_lock:
            is_running = engine_state["running"]

        if not is_running:
            with state_lock:
                engine_state["status"] = "Stopped"
                engine_state["next_post_in"] = 0
            time.sleep(2)
            continue

        with state_lock:
            engine_state["status"] = "Preparing post"

        try:
            item = post_queue.get_next()

            with state_lock:
                engine_state["last_topic"] = item["title"]

            if not BOT_TOKEN:
                raise RuntimeError(
                    "Bot token নেই। Render Environment Variables-এ "
                    "TELEGRAM_BOT_TOKEN সেট করুন।"
                )

            send_telegram_post(item)

            with state_lock:
                engine_state["total_posts"] += 1
                engine_state["last_topic"] = item["title"]
                engine_state["last_post_time"] = datetime.now(
                    timezone(timedelta(hours=6))
                ).strftime("%d-%m-%Y %I:%M:%S %p")
                engine_state["last_error"] = None
                engine_state["status"] = "Running"

            logger.info("Post published: %s", item["title"])

        except Exception as exc:
            logger.exception("Post delivery failed")
            with state_lock:
                engine_state["last_error"] = str(exc)[:500]
                engine_state["status"] = "Error"

        remaining = POST_INTERVAL

        while remaining > 0:
            with state_lock:
                is_running = engine_state["running"]
                engine_state["next_post_in"] = remaining

            if not is_running:
                break

            time.sleep(1)
            remaining -= 1

        with state_lock:
            engine_state["next_post_in"] = 0


# =========================================================
# PROFESSIONAL DASHBOARD
# =========================================================

HTML_TEMPLATE = r"""
<!DOCTYPE html>
<html lang="bn">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="theme-color" content="#070b16">
<meta http-equiv="refresh" content="20">
<title>{{ project_name }}</title>

<style>
:root {
    --bg: #070b16;
    --card: #111a2b;
    --cyan: #38e8ff;
    --green: #39e59b;
    --red: #ff5c78;
    --text: #edf5ff;
    --muted: #91a2bc;
}
* { box-sizing: border-box; }
body {
    margin: 0;
    min-height: 100vh;
    padding: 24px 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--text);
    background:
      radial-gradient(ellipse at top, #142944 0%, transparent 55%),
      radial-gradient(ellipse at bottom right, #19113b 0%, transparent 45%),
      var(--bg);
    font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
}
.container { width: 100%; max-width: 680px; }
.header { text-align: center; margin-bottom: 22px; }
.logo {
    width: 72px; height: 72px; margin: 0 auto 14px;
    border: 1px solid #38e8ff66; border-radius: 22px;
    display: grid; place-items: center; font-size: 34px;
    background: #0b2035;
    box-shadow: 0 0 32px #38e8ff20;
}
h1 { font-size: clamp(22px, 5vw, 31px); margin: 0; }
.accent { color: var(--cyan); }
.subtitle { color: var(--muted); font-size: 13px; margin-top: 9px; }
.card {
    padding: 22px; margin-bottom: 15px;
    border: 1px solid #263850; border-radius: 19px;
    background: linear-gradient(145deg, #142136ee, #0d1424ee);
    box-shadow: 0 16px 45px #0005;
}
.status {
    padding: 12px; border-radius: 10px;
    text-align: center; font-weight: 750; font-size: 13px;
    margin-bottom: 18px;
}
.running { background: #073b2d; color: #62f7b9; }
.stopped { background: #481b29; color: #ff9bab; }
.error { background: #4a3014; color: #ffd48a; }
.grid {
    display: grid; grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 12px;
}
.stat {
    padding: 15px; border-radius: 12px;
    background: #081221; border: 1px solid #26374b;
    min-width: 0;
}
.stat small { color: var(--muted); display: block; margin-bottom: 8px; }
.stat strong { font-size: 16px; overflow-wrap: anywhere; }
.section-title { font-size: 14px; color: var(--cyan); margin: 0 0 14px; }
.topic { line-height: 1.7; overflow-wrap: anywhere; }
.topic small { color: var(--muted); }
.btns { display: flex; gap: 12px; }
button {
    flex: 1; min-height: 46px; padding: 12px;
    border: 0; border-radius: 10px;
    font-weight: 800; font-size: 14px; cursor: pointer;
}
.start { color: #04271b; background: var(--green); }
.stop { color: white; background: #d93455; }
.link {
    display: block; padding: 14px; margin-top: 10px;
    border-radius: 10px; text-align: center;
    text-decoration: none; color: var(--cyan);
    border: 1px solid #38e8ff35; background: #071526;
}
.error-text { color: #ff8e9f; font-size: 12px; overflow-wrap: anywhere; }
.footer { text-align: center; font-size: 12px; color: var(--muted); line-height: 1.9; }
@media (max-width: 420px) {
    .card { padding: 16px; }
    .grid { grid-template-columns: 1fr 1fr; gap: 8px; }
    .stat { padding: 11px; }
    .btns { flex-direction: column; }
}
</style>
</head>

<body>
<div class="container">

    <header class="header">
        <div class="logo">🛡️</div>
        <h1><span class="accent">CYBER TEAM</span> HELP</h1>
        <div class="subtitle">ADVANCED KNOWLEDGE & AUTOMATION CORE</div>
        <div class="subtitle">Developer: {{ developer }}</div>
    </header>

    <section class="card">
        <div class="status {{ 'running' if state.running and not state.last_error else ('error' if state.running else 'stopped') }}">
            {% if state.running and not state.last_error %}
                🟢 ENGINE ACTIVE
            {% elif state.running %}
                🟠 ENGINE ACTIVE — CHECK ERROR
            {% else %}
                🔴 ENGINE PAUSED
            {% endif %}
        </div>

        <div class="grid">
            <div class="stat">
                <small>📨 Successful Posts</small>
                <strong>{{ state.total_posts }}</strong>
            </div>
            <div class="stat">
                <small>⏱️ Post Interval</small>
                <strong>{{ interval_minutes }} min</strong>
            </div>
            <div class="stat">
                <small>📚 Knowledge Topics</small>
                <strong>{{ topic_count }}</strong>
            </div>
            <div class="stat">
                <small>⌛ Next Attempt</small>
                <strong>{{ countdown }}</strong>
            </div>
        </div>
    </section>

    <section class="card">
        <h2 class="section-title">📡 LATEST ENGINE ACTIVITY</h2>
        <div class="topic">
            <small>Latest topic</small><br>
            <strong>{{ state.last_topic }}</strong>
            <br><br>
            <small>Last successful post</small><br>
            <strong>{{ state.last_post_time }}</strong>
            <br><br>
            <small>Engine status</small><br>
            <strong>{{ state.status }}</strong>
        </div>
        {% if state.last_error %}
        <hr style="border-color:#29364a;margin:18px 0">
        <div class="error-text">⚠️ {{ state.last_error }}</div>
        {% endif %}
    </section>

    <section class="card">
        <h2 class="section-title">⚙️ ENGINE CONTROL</h2>
        <form method="POST" action="/control" class="btns">
            <input type="hidden" name="action"
                   value="{{ 'stop' if state.running else 'start' }}">
            <button class="{{ 'stop' if state.running else 'start' }}" type="submit">
                {{ '⏸ PAUSE ENGINE' if state.running else '▶ START ENGINE' }}
            </button>
        </form>
        <p style="font-size:12px;color:var(--muted);line-height:1.7">
            Pause করলে নতুন পোস্ট পাঠানো বন্ধ হবে। Start করলে ইঞ্জিন আবার কাজ শুরু করবে।
        </p>
    </section>

    <section class="card">
        <h2 class="section-title">🌐 OFFICIAL TOOLS & COMMUNITY</h2>
        <a class="link" href="https://cyber-team-help-all-in-one.vercel.app/" target="_blank" rel="noopener">
            🚀 CTH All-in-One Hub
        </a>
        <a class="link" href="https://unlimited-text-generator-cth-2esh.vercel.app/" target="_blank" rel="noopener">
            ⚡ Unlimited Text Generator
        </a>
        <a class="link" href="https://link-to-id-hack-tolls-cth.vercel.app/" target="_blank" rel="noopener">
            🛠️ Link & Account Security Tools
        </a>
        <a class="link" href="{{ group_link }}" target="_blank" rel="noopener">
            👥 JOIN PUBLIC TELEGRAM GROUP
        </a>
        <a class="link" href="{{ private_group_link }}" target="_blank" rel="noopener">
            🔒 JOIN PRIVATE VIP GROUP
        </a>
    </section>

    <footer class="footer">
        🛡️ CYBER TEAM HELP — KNOWLEDGE FOR EVERYONE<br>
        Built with Python & Flask<br>
        Credit: <span class="accent">{{ developer }}</span><br>
        <small>কাজের জন্য ইনবক্সে মেসেজ দিন: {{ developer }}</small>
    </footer>
</div>
</body>
</html>
"""


def dashboard_snapshot():
    with state_lock:
        return dict(engine_state)


@app.route("/")
def home():
    state = dashboard_snapshot()
    seconds = max(0, state["next_post_in"])
    countdown = f"{seconds // 60:02d}:{seconds % 60:02d}"

    return render_template_string(
        HTML_TEMPLATE,
        project_name=PROJECT_NAME,
        developer=DEVELOPER,
        group_link=GROUP_LINK,
        private_group_link=PRIVATE_GROUP_LINK,
        state=state,
        interval_minutes=POST_INTERVAL // 60,
        topic_count=len(POSTS),
        countdown=countdown
    )


@app.route("/health")
def health():
    state = dashboard_snapshot()
    return {
        "ok": True,
        "running": state["running"],
        "status": state["status"],
        "total_posts": state["total_posts"]
    }


@app.route("/control", methods=["POST"])
def control():
    action = request.form.get("action", "")

    with state_lock:
        if action == "start":
            engine_state["running"] = True
            engine_state["last_error"] = None
            engine_state["status"] = "Starting"
            logger.info("Engine start requested from dashboard.")

        elif action == "stop":
            engine_state["running"] = False
            engine_state["status"] = "Stopped"
            logger.info("Engine stop requested from dashboard.")

    return redirect(url_for("home"))


# =========================================================
# WORKER STARTUP
# =========================================================

engine_thread = None
engine_start_lock = threading.Lock()


def start_engine_once():
    global engine_thread

    with engine_start_lock:
        if engine_thread and engine_thread.is_alive():
            return

        engine_thread = threading.Thread(
            target=background_professional_security_engine,
            name="cyber-knowledge-engine",
            daemon=True
        )
        engine_thread.start()


if os.environ.get("WERKZEUG_RUN_MAIN") == "true" or (
    __name__ == "__main__"
):
    start_engine_once()
elif os.environ.get("RENDER"):
    start_engine_once()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "10000"))
    app.run(
        host="0.0.0.0",
        port=port,
        debug=False,
        use_reloader=False
    )
