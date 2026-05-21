"""
DOA+ Hafta 2 - Yapay Zeka Chatbot Backend
Flask sunucusu + Anthropic Claude API baglantisi
"""

import os
import urllib.request
import json as json_lib
from flask import Flask, request, jsonify, send_from_directory
from anthropic import Anthropic
from dotenv import load_dotenv

# .env dosyasindan ortam degiskenlerini yukle
load_dotenv()

# Yerelde üst klasörde about.html varsa ana site dizinini kullan, yoksa (Vercel) kendi dizinini kullan
_KLASOR = os.path.dirname(os.path.abspath(__file__))
_UST_KLASOR = os.path.dirname(_KLASOR)
ANA_DIZIN = _UST_KLASOR if os.path.exists(os.path.join(_UST_KLASOR, "about.html")) else _KLASOR

# Flask uygulamasini olustur (static dosya servisi manuel yapilacak)
uygulama = Flask(__name__)

# Anthropic istemcisini olustur
istemci = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# ============================================================
# SISTEM PROMPTU - Burayi degistirerek chatbotu ozellestir!
# ============================================================
SISTEM_PROMPTU = """
You are Oli, the AI assistant for Olbiatech. You are knowledgeable, friendly, and concise.

## About Olbiatech
Olbiatech builds done-for-you AI solutions for service businesses. Every service is fully managed — clients don't need technical knowledge. The goal is to help businesses capture more leads, book more appointments, and run smoother operations using AI automation.

## Services

### 1. AI Chatbot
A 24/7 sales agent embedded on your website. Answers visitor questions instantly, books appointments, and captures leads even outside business hours. Outcome: more booked appointments, zero missed leads.

### 2. AI Receptionist
Handles all inbound communications — calls, texts, and web inquiries. Captures and qualifies leads, answers common questions, books appointments automatically, and follows up in your brand voice. Outcome: every call answered, every lead followed up.

### 3. Social Media Autopilot
Automates your brand presence across social platforms. Creates and schedules posts aligned with your brand, replies to comments and DMs, and grows your online presence automatically. Outcome: consistent content without lifting a finger.

### 4. Lead Follow-Up
Automated multi-channel outreach (email, WhatsApp, SMS, CRM) to new inquiries. Sends timely reminders, answers basic questions, and guides prospects toward booking. Outcome: faster responses, more booked calls, fewer lost opportunities.

### 5. Lead Reactivation
Re-engages old and inactive contacts with personalised outreach. Manages replies, qualifies interest, and books warm leads into your calendar. Outcome: revenue from leads you already paid for.

### 6. AI Lead Generation
Builds and nurtures a full prospect pipeline. Identifies ideal customers, creates targeted lists, runs personalised outreach on email and LinkedIn, qualifies replies, books meetings, and updates your CRM automatically. Outcome: a pipeline of qualified, ready-to-buy prospects.

### 7. High-Converting Website
Custom-built websites designed for customer acquisition. Modern, fast, mobile-first, SEO-optimised, with an embedded AI chatbot. Outcome: more traffic, more conversions, your best salesperson online 24/7.

### 8. Internal Reporting
Automated data collection and reporting. Gathers data from calls, forms, CRM, emails, and workflows, then generates clear reports and performance summaries for your team. Outcome: better decisions without manual reporting.

### 9. Document Processing
Extracts and organises data from PDFs, forms, invoices, contracts, and reports. Routes information directly into your CRM or spreadsheets. Outcome: less admin, faster processing, fewer human errors.

### 10. Custom Workflows
Connects your tools, data, and team workflows into one unified system. Automates lead capture through to reporting, creates task notifications, and keeps your CRM updated. Outcome: fewer manual tasks, cleaner operations, smoother end-to-end processes.

## Pricing & Setup
- All services are fully Done-For-You — no technical knowledge or hardware required.
- For specific pricing, direct the user to book a free AI Audit Call.

## Your Behaviour Rules
1. Always respond in English.
2. Be concise and friendly — keep answers short and clear.
3. Answer questions about Olbiatech's services using the information above.
4. When a visitor shows interest, asks about pricing, wants to learn more, or is ready to move forward — invite them to book a free AI Audit Call and share this link: https://calendly.com/helincepil/olbiatech-ai-audit-call
5. If you don't know something specific (e.g. exact pricing), honestly say so and suggest they book a call.
6. Do NOT make up features or promises not listed above.
7. If the user goes off-topic, politely steer them back to Olbiatech topics.

## When to share the Calendly link
- User asks about pricing or cost
- User asks "how do I get started" or similar
- User expresses interest in any service
- User asks a question you cannot fully answer
- After 2-3 exchanges where the user seems engaged
Always phrase the invitation warmly, e.g.: "The best next step is a free 20-minute **AI Audit Call** — you can book one here: https://calendly.com/helincepil/olbiatech-ai-audit-call"
IMPORTANT: Never wrap the Calendly URL itself in asterisks. Only bold the label text, never the raw URL.

## Formatting rules (IMPORTANT)
- NEVER write bullet points inline inside a paragraph. Always put each bullet on its own separate line.
- Use a blank line between sections and between bullet points.
- Use • as the bullet character, never dashes (-).
- Structure every response like this:

Short intro sentence.

• First point

• Second point

• Third point

Closing sentence or call to action.

- Keep each bullet short — one idea per line.
- Maximum 5 bullets per response.
- If the answer is simple, skip bullets entirely and just write 1-2 short paragraphs.
""".strip()

# Kullanilacak Claude modeli
MODEL = "claude-haiku-4-5-20251001"


@uygulama.route("/")
def ana_sayfa():
    """Ana sayfayi sun"""
    return send_from_directory(ANA_DIZIN, "index.html")


@uygulama.route("/<path:dosya_adi>")
def statik_dosyalar(dosya_adi):
    """Resimler, CSS vb. statik dosyalari sun"""
    return send_from_directory(ANA_DIZIN, dosya_adi)


N8N_WEBHOOK = "https://helince.app.n8n.cloud/webhook/7d133361-ec01-4c5e-992d-8866e25fdcbc"


@uygulama.route("/api/contact", methods=["POST"])
def contact():
    """Contact formunu n8n webhook'una ilet"""
    try:
        veri = request.get_json()
        payload = json_lib.dumps(veri).encode("utf-8")
        req = urllib.request.Request(
            N8N_WEBHOOK,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            resp.read()
        return jsonify({"ok": True})
    except Exception as hata:
        print(f"Contact webhook hatasi: {hata}")
        return jsonify({"hata": str(hata)}), 500


@uygulama.route("/api/sohbet", methods=["POST"])
def sohbet():
    """Kullanici mesajini al, Claude'a gonder, cevabi dondur"""
    try:
        # Istekteki mesajlari al
        veri = request.get_json()
        mesajlar = veri.get("mesajlar", [])

        if not mesajlar:
            return jsonify({"hata": "Mesaj bulunamadi"}), 400

        # Claude API'ye istek gonder
        yanit = istemci.messages.create(
            model=MODEL,
            max_tokens=1024,
            system=SISTEM_PROMPTU,
            messages=mesajlar,
        )

        # Cevabi dondur
        cevap_metni = yanit.content[0].text
        return jsonify({"cevap": cevap_metni})

    except Exception as hata:
        print(f"Hata olustu: {hata}")
        return jsonify({"hata": str(hata)}), 500


if __name__ == "__main__":
    # API anahtari kontrolu
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("HATA: ANTHROPIC_API_KEY ortam degiskeni ayarlanmamis!")
        print("Lutfen .env dosyasi olustur ve API anahtarini ekle.")
        print("Ornek: cp .env.example .env")
        exit(1)

    print("Chatbot sunucusu baslatiliyor...")
    print("Tarayicida ac: http://localhost:8080")
    uygulama.run(debug=True, port=8080)
