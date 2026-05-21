# DOA+ Hafta 2 - Yapay Zeka Chatbot

## Proje Hakkinda

Bu, Flask + Anthropic Claude API kullanan bir musteri destek chatbot projesidir. DOA+ egitim programinin 2. hafta odevidir.

## Dosya Yapisi

- `index.html` — Sohbet arayuzu (tek sayfa, koyu tema)
- `style.css` — Koyu tema stilleri
- `app.js` — Frontend sohbet mantigi, `/api/sohbet` endpoint'ine POST istegi gonderir
- `server.py` — Flask backend, Claude API baglantisi, sistem promptu burada tanimli
- `requirements.txt` — Python bagimliliklari
- `.env` — API anahtari (git'e eklenmez)

## Mimari

Frontend (index.html + app.js) mesajlari JSON olarak `/api/sohbet` endpoint'ine gonderir. Backend (server.py) bu mesajlari Claude API'ye iletir ve cevabi dondurur. Tum sohbet gecmisi frontend tarafinda tutulur ve her istekte gonderilir.

## Onemli Noktalar

- Sistem promptu `server.py` icindeki `SISTEM_PROMPTU` degiskeninde. Chatbotun davranisini degistirmek icin burayi duzenle.
- Model ayari `MODEL` degiskeninde.
- API anahtari `.env` dosyasindan okunur, asla koda yazilmaz.
- Turkce degisken ve fonksiyon isimleri kullanilmistir.

## Calistirma

```bash
pip install -r requirements.txt
cp .env.example .env  # API anahtarini gir
python server.py
```

## Yaygin Degisiklikler

- Farkli bir sektore uyarlamak icin `SISTEM_PROMPTU` degerini degistir
- Farkli bir model kullanmak icin `MODEL` degerini degistir
- Arayuzu ozellestirmek icin `style.css` dosyasini duzenle
