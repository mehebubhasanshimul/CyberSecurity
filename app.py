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
# CYBER TEAM HELP - ADVANCED KNOWLEDGE BOT
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
DEVELOPER = "@SHADOW_JOKER_CTH"
PROJECT_NAME = "CYBER TEAM HELP | Advanced Knowledge Core"

POST_INTERVAL = max(
    60, int(os.getenv("POST_INTERVAL", "1200"))
)

REQUEST_TIMEOUT = 25

CYBER_GIFS = [
    "https://media.giphy.com/media/w4zX4PfkQmZ4xeG7ny/giphy.gif",
    "https://media.giphy.com/media/WWIvZaHUJEOWi5UhGV/giphy.gif",
    "https://media.giphy.com/media/xTiTnMhJTwNHChdTZS/giphy.gif",
    "https://media.giphy.com/media/W23kW9Z07sQ3p7xS5j/giphy.gif",
]

# =========================================================
# KNOWLEDGE BASE
# Account recovery, VPN, ethical hacking, programming
# =========================================================

POSTS = [
    {
        "category": "🛡️ VPN & PRIVACY",
        "title": "VPN কী এবং কীভাবে নিরাপদে ব্যবহার করবেন?",
        "content": (
            "VPN আপনার ডিভাইস ও VPN সার্ভারের মধ্যে এনক্রিপ্টেড "
            "সংযোগ তৈরি করতে পারে। তবে VPN আপনাকে সম্পূর্ণ "
            "অদৃশ্য করে না এবং সব ধরনের ট্র্যাকিং বন্ধ করে না।\n\n"
            "✅ বিশ্বস্ত VPN provider নির্বাচন করুন।\n"
            "✅ Privacy policy ও logging policy পড়ুন।\n"
            "✅ Kill switch এবং DNS leak protection দেখুন।\n"
            "✅ অজানা ফ্রি VPN-এ সংবেদনশীল তথ্য দেবেন না।\n"
            "✅ HTTPS ও two-factor authentication ব্যবহার করুন।"
        ),
        "tool": "Proton VPN / WireGuard",
        "link": "https://www.wireguard.com/",
        "safety": "নিজের ডিভাইস ও নেটওয়ার্কের নিরাপত্তায় ব্যবহার করুন।"
    },
    {
        "category": "🔐 ACCOUNT RECOVERY",
        "title": "Facebook Disabled Account Recovery Guide",
        "content": (
            "Facebook account disabled হলে প্রথমে লগইন করে "
            "দেখুন review বা appeal option দেওয়া হয়েছে কি না।\n\n"
            "১. অ্যাকাউন্টে দেখানো নির্দেশনা অনুসরণ করুন।\n"
            "২. প্রয়োজন হলে নিজের পরিচয়পত্রের তথ্য সঠিকভাবে দিন।\n"
            "৩. ইমেইল ও notification পরীক্ষা করুন।\n"
            "৪. অফিসিয়াল Help Center ব্যবহার করুন।\n"
            "৫. ভুয়া recovery service-কে টাকা বা password দেবেন না।\n\n"
            "মনে রাখবেন: আপিল করলেই অ্যাকাউন্ট ফেরত পাওয়ার নিশ্চয়তা নেই।"
        ),
        "tool": "Facebook Help Center",
        "link": "https://www.facebook.com/help/",
        "safety": "শুধু নিজের অ্যাকাউন্টের জন্য আবেদন করুন।"
    },
    {
        "category": "🔐 ACCOUNT RECOVERY",
        "title": "Instagram Suspended Account Review",
        "content": (
            "Instagram account suspended হলে অ্যাপে লগইন করে "
            "Appeal, Request Review অথবা প্রদর্শিত নির্দেশনা অনুসরণ করুন।\n\n"
            "✅ নিজের ইমেইল ও ফোন নম্বরের অ্যাক্সেস রাখুন।\n"
            "✅ অফিসিয়াল security notification যাচাই করুন।\n"
            "✅ পরিচয় যাচাই চাইলে সঠিক তথ্য দিন।\n"
            "✅ অ্যাকাউন্ট compromise হয়ে থাকলে secure করুন।\n"
            "❌ কাউকে password বা login code দেবেন না।"
        ),
        "tool": "Instagram Help Center",
        "link": "https://help.instagram.com/",
        "safety": "কোনো recovery agent-কে login code দেবেন না।"
    },
    {
        "category": "🔐 ACCOUNT SECURITY",
        "title": "Facebook বা Instagram Hack হলে করণীয়",
        "content": (
            "নিজের অ্যাকাউন্টে অননুমোদিত প্রবেশের সন্দেহ হলে "
            "দ্রুত নিরাপত্তা ব্যবস্থা নিন।\n\n"
            "১. অফিসিয়াল account recovery পেজ ব্যবহার করুন।\n"
            "২. ইমেইল অ্যাকাউন্টের password পরিবর্তন করুন।\n"
            "৩. অচেনা session ও connected apps সরিয়ে দিন।\n"
            "৪. Two-factor authentication চালু করুন।\n"
            "৫. ইমেইল ও ফোন নম্বর ঠিক আছে কি না দেখুন।"
        ),
        "tool": "Meta Account Security",
        "link": "https://www.facebook.com/hacked",
        "safety": "অন্যের অ্যাকাউন্টে প্রবেশের চেষ্টা করবেন না।"
    },
    {
        "category": "💻 ETHICAL HACKING",
        "title": "Ethical Hacking শেখার সঠিক রোডম্যাপ",
        "content": (
            "Ethical hacking শিখতে প্রথমে networking, Linux, "
            "HTTP, DNS ও web application-এর ভিত্তি বুঝুন।\n\n"
            "📌 ধাপ ১: TCP/IP ও networking basics।\n"
            "📌 ধাপ ২: Linux terminal ও file permissions।\n"
            "📌 ধাপ ৩: Python scripting।\n"
            "📌 ধাপ ৪: Web security ও OWASP Top 10।\n"
            "📌 ধাপ ৫: অনুমোদিত lab-এ vulnerability testing।\n\n"
            "অনুমতি ছাড়া কোনো ওয়েবসাইট বা নেটওয়ার্ক পরীক্ষা করবেন না।"
        ),
        "tool": "PortSwigger Web Security Academy",
        "link": "https://portswigger.net/web-security",
        "safety": "শুধু অনুমোদিত ল্যাব ও সিস্টেমে অনুশীলন করুন।"
    },
    {
        "category": "🌐 NETWORK SECURITY",
        "title": "Nmap Network Scanning Fundamentals",
        "content": (
            "Nmap নেটওয়ার্কে host discovery এবং service auditing-এর "
            "জন্য বহুল ব্যবহৃত একটি ওপেন-সোর্স টুল।\n\n"
            "শিখুন:\n"
            "• IP address ও subnet কী।\n"
            "• TCP এবং UDP-এর পার্থক্য।\n"
            "• Port ও service কীভাবে কাজ করে।\n"
            "• Scan result কীভাবে ব্যাখ্যা করতে হয়।\n\n"
            "নিজের lab বা অনুমোদিত নেটওয়ার্কে পরীক্ষা করুন।"
        ),
        "tool": "Nmap",
        "link": "https://nmap.org/book/",
        "safety": "অনুমতি ছাড়া public IP scan করবেন না।"
    },
    {
        "category": "🧪 WEB SECURITY",
        "title": "SQL Injection প্রতিরোধের উপায়",
        "content": (
            "SQL Injection ঘটে যখন user input অনিরাপদভাবে "
            "database query-তে যুক্ত করা হয়।\n\n"
            "প্রতিরোধ:\n"
            "✅ Parameterized queries ব্যবহার করুন।\n"
            "✅ Database account-এ minimum permissions দিন।\n"
            "✅ Input validation ও error handling করুন।\n"
            "✅ Database credentials source code-এ রাখবেন না।\n"
            "✅ নিরাপদ test environment-এ security test করুন।"
        ),
        "tool": "OWASP SQL Injection Guide",
        "link": "https://owasp.org/www-community/attacks/SQL_Injection",
        "safety": "শুধু নিজের অ্যাপ বা অনুমোদিত lab-এ পরীক্ষা করুন।"
    },
    {
        "category": "🧪 WEB SECURITY",
        "title": "XSS Vulnerability ও Browser Security",
        "content": (
            "Cross-Site Scripting বা XSS-এর মাধ্যমে অনিরাপদ "
            "ওয়েব পেজে ক্ষতিকর script চালানো সম্ভব হতে পারে।\n\n"
            "প্রতিরোধের কৌশল:\n"
            "• Context-aware output encoding।\n"
            "• নিরাপদ template rendering।\n"
            "• Content Security Policy (CSP)।\n"
            "• Untrusted HTML sanitize করা।\n"
            "• Dependency নিয়মিত আপডেট করা।"
        ),
        "tool": "OWASP Cross Site Scripting",
        "link": "https://owasp.org/www-community/attacks/xss/",
        "safety": "নিজস্ব অ্যাপ ও অনুমোদিত security lab-এ শিখুন।"
    },
    {
        "category": "🐍 PYTHON PROGRAMMING",
        "title": "Python শেখার Beginner Roadmap",
        "content": (
            "Python দিয়ে automation, web development, data analysis "
            "ও defensive security tools তৈরি করা যায়।\n\n"
            "শুরু করুন:\n"
            "১. Variables, strings ও numbers।\n"
            "২. If/else এবং loops।\n"
            "৩. Functions ও modules।\n"
            "৪. Lists, dictionaries ও sets।\n"
            "৫. Exceptions ও file handling।\n"
            "৬. Requests, JSON ও API basics।\n"
            "৭. ছোট automation project তৈরি করুন।"
        ),
        "tool": "Official Python Tutorial",
        "link": "https://docs.python.org/3/tutorial/",
        "safety": "API key ও password কখনো public repository-তে রাখবেন না।"
    },
    {
        "category": "📱 TERMUX & LINUX",
        "title": "Termux নিরাপদভাবে ব্যবহার করার টিপস",
        "content": (
            "Termux হলো Android-এ Linux command-line environment "
            "ব্যবহারের একটি উপায়।\n\n"
            "দরকারি অভ্যাস:\n"
            "✅ অফিসিয়াল ও বিশ্বস্ত উৎস থেকে Termux ইনস্টল করুন।\n"
            "✅ Package নিয়মিত update করুন।\n"
            "✅ অপরিচিত shell script চালানোর আগে পড়ে নিন।\n"
            "✅ অপ্রয়োজনীয় storage permission দেবেন না।\n"
            "✅ গুরুত্বপূর্ণ ফাইলের backup রাখুন।\n\n"
            "Root ছাড়া অনেক development ও scripting কাজ করা যায়।"
        ),
        "tool": "Termux Documentation",
        "link": "https://termux.dev/",
        "safety": "অপরিচিত script-কে অন্ধভাবে root permission দেবেন না।"
    },
    {
        "category": "🔑 PASSWORD SECURITY",
        "title": "Strong Password ও 2FA Protection",
        "content": (
            "একটি অ্যাকাউন্টের password অন্য অ্যাকাউন্টে পুনরায় "
            "ব্যবহার করলে credential leak-এর ঝুঁকি বাড়ে।\n\n"
            "🔒 প্রতিটি অ্যাকাউন্টে আলাদা password রাখুন।\n"
            "🔒 Password manager ব্যবহার করতে পারেন।\n"
            "🔒 Authenticator-based 2FA বা passkey চালু করুন।\n"
            "🔒 Recovery code নিরাপদ স্থানে রাখুন।\n"
            "🔒 সন্দেহজনক login alert পরীক্ষা করুন।"
        ),
        "tool": "CISA Secure Our World",
        "link": "https://www.cisa.gov/secure-our-world",
        "safety": "কাউকে OTP, recovery code বা password দেবেন না।"
    },
    {
        "category": "🦠 MALWARE DEFENSE",
        "title": "Ransomware থেকে ফাইল সুরক্ষিত রাখুন",
        "content": (
            "Ransomware গুরুত্বপূর্ণ ফাইল ব্যবহার-অযোগ্য করে দিতে পারে। "
            "প্রতিরোধের জন্য layered security জরুরি।\n\n"
            "• Offline বা immutable backup রাখুন।\n"
            "• Operating system আপডেট রাখুন।\n"
            "• অজানা attachment খুলবেন না।\n"
            "• Standard user account ব্যবহার করুন।\n"
            "• Restore করার আগে backup যাচাই করুন।\n"
            "• Incident হলে আক্রান্ত ডিভাইস নেটওয়ার্ক থেকে বিচ্ছিন্ন করুন।"
        ),
        "tool": "CISA Stop Ransomware",
        "link": "https://www.cisa.gov/stopransomware",
        "safety": "সন্দেহজনক ফাইল নিরাপদ পরিবেশ ছাড়া চালাবেন না।"
    },
    {
        "category": "📡 NETWORKING",
        "title": "DNS, IP Address ও HTTPS সহজ ব্যাখ্যা",
        "content": (
            "IP address নেটওয়ার্কে একটি device বা interface-কে "
            "চিহ্নিত করতে সাহায্য করে। DNS domain name-কে IP address-এ "
            "resolve করে। HTTPS browser ও server-এর মধ্যে "
            "encrypted connection তৈরি করে।\n\n"
            "অনুশীলন করুন:\n"
            "• Private ও public IP-এর পার্থক্য।\n"
            "• DNS resolver কীভাবে কাজ করে।\n"
            "• TLS certificate যাচাই।\n"
            "• Router ও firewall-এর ভূমিকা।"
        ),
        "tool": "Cloudflare Learning Center",
        "link": "https://www.cloudflare.com/learning/",
        "safety": "Public Wi-Fi-তে সংবেদনশীল কাজের সময় সতর্ক থাকুন।"
    },
    {
        "category": "🔍 OSINT & PRIVACY",
        "title": "OSINT ও Digital Footprint Protection",
        "content": (
            "OSINT হলো আইনসম্মতভাবে প্রকাশ্য উৎস থেকে তথ্য সংগ্রহ "
            "ও বিশ্লেষণ করার পদ্ধতি। এটি security research-এ কাজে লাগে।\n\n"
            "নিজের privacy রক্ষায়:\n"
            "• Public profile-এর তথ্য পর্যালোচনা করুন।\n"
            "• ছবি শেয়ার করার আগে location metadata দেখুন।\n"
            "• অপ্রয়োজনীয় app permissions বন্ধ করুন।\n"
            "• পুরোনো public posts পরীক্ষা করুন।\n"
            "• অন্যের ব্যক্তিগত তথ্য অনুমতি ছাড়া প্রকাশ করবেন না।"
        ),
        "tool": "OSINT Framework",
        "link": "https://osintframework.com/",
        "safety": "গোপনীয়তা, সম্মতি ও প্রযোজ্য আইন মেনে চলুন।"
    },
    {
        "category": "🧰 SECURITY TOOLS",
        "title": "Wireshark দিয়ে Network Traffic শেখা",
        "content": (
            "Wireshark packet capture ও protocol analysis-এর "
            "জন্য ব্যবহৃত একটি network analyzer।\n\n"
            "শিখতে পারেন:\n"
            "• Packet, frame ও protocol।\n"
            "• TCP handshake।\n"
            "• DNS request ও response।\n"
            "• TLS traffic-এর মৌলিক ধারণা।\n"
            "• Network troubleshooting।\n\n"
            "Capture করার আগে নেটওয়ার্কের মালিকের অনুমতি নিন।"
        ),
        "tool": "Wireshark",
        "link": "https://www.wireshark.org/docs/",
        "safety": "অন্যের private traffic অনুমতি ছাড়া capture করবেন না।"
    },
    {
        "category": "🌍 WEB DEVELOPMENT",
        "title": "HTML, CSS ও JavaScript দিয়ে ওয়েবসাইট",
        "content": (
            "একটি সুন্দর responsive website তৈরিতে তিনটি মূল প্রযুক্তি "
            "গুরুত্বপূর্ণ:\n\n"
            "HTML: পেজের structure।\n"
            "CSS: layout, color ও responsive design।\n"
            "JavaScript: interaction ও dynamic behavior।\n\n"
            "শুরুতে একটি portfolio, calculator বা personal dashboard "
            "তৈরি করুন। পরে API integration ও accessibility শিখুন।"
        ),
        "tool": "MDN Web Docs",
        "link": "https://developer.mozilla.org/",
        "safety": "User input ও API data নিরাপদভাবে handle করুন।"
    },
    {
        "category": "🤖 AI & AUTOMATION",
        "title": "Python দিয়ে নিরাপদ Automation",
        "content": (
            "Python দিয়ে repetitive কাজ স্বয়ংক্রিয় করা যায়।\n\n"
            "Project idea:\n"
            "• নিজের ফাইল গুছিয়ে রাখার script।\n"
            "• Website uptime checker।\n"
            "• CSV report generator।\n"
            "• Telegram notification bot।\n"
            "• নিজের server-এর log analyzer।\n\n"
            "Error handling, logging ও environment variables "
            "ব্যবহার করতে শিখুন।"
        ),
        "tool": "Python Logging Documentation",
        "link": "https://docs.python.org/3/library/logging.html",
        "safety": "Automation-এ rate limits ও service terms মানুন।"
    },
    {
        "category": "🧪 SECURITY LAB",
        "title": "OWASP ZAP দিয়ে Web Security Testing",
        "content": (
            "OWASP ZAP একটি ওপেন-সোর্স web application security "
            "testing tool। Beginner-রা এর passive scanning ও "
            "training lab দিয়ে শুরু করতে পারেন।\n\n"
            "প্রথমে নিজের local test application চালান।\n"
            "Scan result যাচাই করে false positive বুঝুন।\n"
            "প্রতিটি finding-এর remediation শিখুন।\n"
            "Production website পরীক্ষা করতে লিখিত অনুমতি নিন।"
        ),
        "tool": "OWASP ZAP",
        "link": "https://www.zaproxy.org/",
        "safety": "অনুমোদিত অ্যাপেই active testing করুন।"
    },
    {
        "category": "🔐 ACCOUNT SAFETY",
        "title": "Suspended Account Appeal: Scam থেকে সাবধান",
        "content": (
            "কেউ যদি বলে টাকা দিলেই Facebook বা Instagram "
            "অ্যাকাউন্ট নিশ্চিতভাবে ফিরিয়ে দেবে, সতর্ক থাকুন।\n\n"
            "✅ অফিসিয়াল appeal flow ব্যবহার করুন।\n"
            "✅ অ্যাকাউন্টের সঙ্গে যুক্ত ইমেইল সুরক্ষিত রাখুন।\n"
            "✅ প্রয়োজনীয় notice ও case reference সংরক্ষণ করুন।\n"
            "❌ Password, OTP বা session cookie শেয়ার করবেন না।\n"
            "❌ ভুয়া support account-কে বিশ্বাস করবেন না।\n\n"
            "Review-এর ফলাফল প্ল্যাটফর্মের সিদ্ধান্তের ওপর নির্ভর করে।"
        ),
        "tool": "Meta Help Center",
        "link": "https://www.facebook.com/help/",
        "safety": "শুধু বৈধ ও অফিসিয়াল recovery পদ্ধতি অনুসরণ করুন।"
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

        # Avoid repeating the previous cycle's final topic immediately.
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
    Send an optional GIF and then the complete formatted post.
    The complete post is sent as a text message, avoiding the
    smaller animation-caption character limit.
    """

    title = html.escape(item["title"])
    category = html.escape(item["category"])
    content = html.escape(item["content"])
    tool = html.escape(item["tool"])
    link = html.escape(item["link"], quote=True)
    safety = html.escape(item["safety"])
    developer = html.escape(DEVELOPER)
    group_link = html.escape(GROUP_LINK, quote=True)

    now = datetime.now(
        timezone(timedelta(hours=6))
    ).strftime("%d-%m-%Y | %I:%M %p")

    message = (
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🛡️ <b>CYBER TEAM HELP</b>\n"
        "⚡ <b>DAILY KNOWLEDGE & SECURITY HUB</b>\n"
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
        f"👥 <a href=\"{group_link}\">JOIN CYBER TEAM HELP</a>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "💡 <i>শিখুন • নিরাপদ থাকুন • দায়িত্বশীল হোন</i>"
    )

    # GIF is optional; a GIF failure must not prevent the text post.
    gif_sent = False
    if CYBER_GIFS:
        selected_gif = random.choice(CYBER_GIFS)

        try:
            telegram_api("sendAnimation", {
                "chat_id": CHAT_ID,
                "animation": selected_gif,
                "caption": (
                    "🛡️ <b>CYBER TEAM HELP</b>\n"
                    "📚 Cybersecurity • Programming • Privacy\n"
                    f"👨‍💻 {developer}"
                ),
                "parse_mode": "HTML"
            })
            gif_sent = True

        except Exception as exc:
            logger.warning("GIF delivery failed: %s", exc)

    # Always attempt to send the full educational content.
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

        # Countdown is interruptible by the dashboard Start/Stop control.
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
.container { width: 100%; max-width: 650px; }
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
            Pause করলে নতুন পোস্ট পাঠানো বন্ধ হবে। Start করলে
            ইঞ্জিন আবার কাজ শুরু করবে।
        </p>
    </section>

    <section class="card">
        <h2 class="section-title">🌐 OFFICIAL COMMUNITY</h2>
        <a class="link" href="{{ group_link }}" target="_blank" rel="noopener">
            👥 JOIN TELEGRAM GROUP
        </a>
        <a class="link" href="https://owasp.org/" target="_blank" rel="noopener">
            🛡️ OWASP SECURITY RESOURCES
        </a>
        <a class="link" href="https://portswigger.net/web-security"
           target="_blank" rel="noopener">
            🧪 WEB SECURITY ACADEMY
        </a>
    </section>

    <footer class="footer">
        🛡️ CYBER TEAM HELP — KNOWLEDGE FOR EVERYONE<br>
        Built with Python & Flask<br>
        Credit: <span class="accent">{{ developer }}</span><br>
        <small>Educational content • Privacy • Responsible Security</small>
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


# Render runs app.py as a normal process. The WERKZEUG condition
# also avoids starting the worker twice in Flask debug mode.
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
