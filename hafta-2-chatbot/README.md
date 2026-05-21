# DOA+ Hafta 2: Yapay Zeka Chatbot

Bu proje, Anthropic Claude API kullanarak calisan bir musteri destek chatbotu icermektedir. Sifirdan yazilmis, basit ve anlasilir bir projedir.

## Ne Yapar?

- Kullanici mesaj yazar, yapay zeka cevap verir
- Musteri destek senaryolarina uygun cevaplar uretir
- Sistem promptu degistirilerek herhangi bir is icin ozellestirilebilir

## Gereksinimler

- Python 3.8+
- Anthropic API anahtari (https://console.anthropic.com adresinden alinir)

## Kurulum

1. Gerekli kutuphaneleri yukle:

```bash
pip install -r requirements.txt
```

2. `.env.example` dosyasini `.env` olarak kopyala ve API anahtarini yaz:

```bash
cp .env.example .env
# .env dosyasini ac ve ANTHROPIC_API_KEY degerini gir
```

3. Sunucuyu baslat:

```bash
python server.py
```

4. Tarayicida ac:

```
http://localhost:5000
```

## Dosya Yapisi

```
hafta-2-chatbot/
├── README.md          # Bu dosya
├── CLAUDE.md          # Claude Code icin proje talimatlari
├── index.html         # Sohbet arayuzu
├── style.css          # Koyu tema stilleri
├── app.js             # Frontend sohbet mantigi
├── server.py          # Flask backend + Claude API baglantisi
├── requirements.txt   # Python bagimliliklari
├── .env.example       # Ornek ortam degiskenleri
└── .env               # Senin API anahtarin (git'e eklenmez)
```

## Ozellestirme

`server.py` dosyasindaki `SISTEM_PROMPTU` degiskenini degistirerek chatbotu farkli bir is icin uyarlayabilirsin. Ornegin:

- Restoran siparis botu
- E-ticaret destek botu
- Randevu alma botu
- Egitim danismani botu

## Sorun Giderme

- **API anahtari hatasi**: `.env` dosyasinda `ANTHROPIC_API_KEY` degerinin dogru yazildigindan emin ol
- **Port kullaniliyor hatasi**: Baska bir terminal `server.py` calistiriyor olabilir, onu kapat
- **Modul bulunamadi hatasi**: `pip install -r requirements.txt` komutunu tekrar calistir
