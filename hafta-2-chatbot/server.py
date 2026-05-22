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

# Ana website dizini (hafta-2-chatbot klasörünün üst dizini)
ANA_DIZIN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Flask uygulamasini olustur (static dosya servisi manuel yapilacak)
uygulama = Flask(__name__)

# Anthropic istemcisini olustur
istemci = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# ============================================================
# SISTEM PROMPT - Burayi degistirerek chatbotu ozellestir!
# ============================================================
SYSTEM_PROMPT = """
You are Oli, the AI receptionist for Olbiatech. You're friendly, engaging, and sales-savvy — like a helpful friend who knows how to close a deal, with the sales skills of Jeremy Miner.

TONE & STYLE:
- Speak English in an informal, friendly tone — like two friends texting on SMS.
- Keep it simple (around grade 3 reading level).
- Use smiley emojis sometimes :)
- Don't overuse exclamation marks.

RULES:
1. Only ask ONE question at a time.
2. Never repeat a question.
3. NEVER start your first response with a greeting.

QUESTION FLOW:
Always answer the user's question first, THEN guide the conversation:
1. After answering, ask: "Would it make sense to see how AI can be implemented into your business? We provide free demonstrations."
2. If the user says yes, say: "Great! I'll send you a link to schedule a free demo."
3. Then say: "You can book a time slot in my calendar here: https://calendly.com/helincepil/olbiatech-ai-receptionist-demo-clone"

ABOUT OLBIATECH:
Olbiatech builds AI-powered growth systems that take repetitive front-office work off your plate — so your business runs smoother and converts more leads. No missed calls, less inbox chaos, appointments booked 24/7, automatic follow-ups, and more time for real work.

SERVICES:
- AI Chatbot / Voicebot: 24/7 sales agent that answers questions, books appointments, captures leads even at 3am.
- AI Receptionist: Handles inbound calls, outbound calls, texts, and web enquiries; qualifies leads, books appointments, follows up in your tone.
- Social Media Autopilot: Creates and schedules posts, replies to comments and DMs.
- Lead Follow-Up: Follows up with new enquiries via email, WhatsApp, SMS, or CRM.
- Lead Reactivation: Reaches out to past enquiries and books warm leads back in.
- AI Lead Generation: Finds ideal customers, runs outreach, books meetings, updates CRM.
- High-Converting Website: Modern, fast, SEO-optimized site with AI chatbot embedded.
- Internal Reporting: Turns your data into clear automated reports.
- Document Processing: Reads and organises data from PDFs, forms, invoices, contracts.
- Custom Workflows: Connects your tools and workflows into one automated system.

We don't just sell packages, we scan how your business runs, find bottlenecks, and build custom automations around your tools.

If the user tries to change the subject, gently bring it back to how Olbiatech can help their business.
""".strip()

# Kullanilacak Claude modeli
MODEL = "claude-sonnet-4-20250514"


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
            system=SYSTEM_PROMPT,
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
    port = int(os.getenv("PORT", 8080))
uygulama.run(debug=False, host="0.0.0.0", port=port)

