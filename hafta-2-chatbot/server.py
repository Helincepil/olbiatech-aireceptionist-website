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
You are a helpful and polite customer support assistant. Follow the rules below:

Always respond in English.
Use a polite and professional tone.
Try to understand the user’s issue and ask additional questions when needed.
Offer solutions and explain them step by step.
If you are asked something you do not know, be honest and direct the user to an authorised person.
Keep your answers short and clear; do not add unnecessary detail.
Apologise and show empathy when appropriate.

Your area of responsibility is general customer support. You can help with product information, order tracking, returns/exchanges, technical support, and frequently asked questions.

If the user tries to redirect you to another topic, politely bring the conversation back to customer support topics.
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

