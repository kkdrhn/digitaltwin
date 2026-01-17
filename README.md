# MyTwin RAG: Dijital İkiz Asistanı & Stil Dönüştürücü 🦾

MyTwin, WhatsApp sohbet geçmişinizi kullanarak sizin üslubunuzu, şakalarınızı ve konuşma reflekslerinizi taklit eden çok yönlü bir dijital ikiz asistanıdır. Google Gemini API (Gemini-3-Flash) ve ChromaDB (Vektör Veri Tabanı) kullanarak çalışır.

## 🚀 Özellikler

- **Çift Modlu Deneyim:**
    - **Cevaplayıcı (Chat):** Twin ile karşılıklı sohbet edin. Sizin geçmiş mesajlarınızdan (RAG) beslenir ve mevcut konuyu (Memory) unutmaz.
    - **Yeniden Üretici (Rewrite):** Herhangi bir metni Twin'in karakteristik üslubuyla yeniden yazın.
- **WhatsApp Mesaj İşleme:** `wpchat.txt` dosyasındaki karmaşık logları temizler ve anlamlı bloklara dönüştürür.
- **RAG (Retrieval-Augmented Generation):** Sadece modelin bilgisiyle değil, *sizin gerçek mesajlarınızla* beslenen dinamik bir zeka.
- **Modern Web Arayüzü:** FastAPI tabanlı, premium karanlık tema ve kolay mod geçişi sağlayan kullanıcı dostu arayüz.

## 🛠 Kurulum

1. **Depoyu klonlayın:**
   ```bash
   git clone https://github.com/kkdrhn/digitaltwin.git
   cd digitaltwin
   ```

2. **Sanal ortam oluşturun ve bağımlılıkları yükleyin:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows için: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **API Anahtarlarınızı ayarlayın:**
   `.env.example` dosyasını `.env` olarak kopyalayın ve Google Gemini API anahtarınızı ekleyin.
   ```bash
   cp .env.example .env
   ```

## 📖 Kullanım Rehberi

### Adım 1: Mesajları Hazırlama
WhatsApp'tan dışa aktardığınız `.txt` dosyasının adını `wpchat.txt` olarak değiştirip ana dizine koyun. 

> [!IMPORTANT]
> **Yapılandırma:** `whatsapp_parser.py` dosyasını açın ve en üstteki `MY_WHATSAPP_NAME` değişkenine WhatsApp'ta kendi kullandığınız ismi (mesajların başında görünen isim, örn: "Ahmet", "Can", ".") yazın.

Ardından parser'ı çalıştırın:
```bash
python whatsapp_parser.py
```

### Adım 2: Vektörleştirme (İndeksleme)
Mesajlarınızı anlamsal olarak veri tabanına kaydetmek için:
```bash
python ingest.py
```

### Adım 3: Çalıştırma
Web arayüzünü başlatmak için:
```bash
python app.py
```

<img width="2940" height="1538" alt="image" src="https://github.com/user-attachments/assets/c1dce1f1-5b58-4d64-8f86-340f9f536ebf" />


Ardından tarayıcınızdan `http://localhost:8000` adresine gidin. Artık hazırsınız!

## 📂 Proje Yapısı

- `whatsapp_parser.py`: WhatsApp loglarını temizleyen parser.
- `ingest.py`: Mesajları vektörleştirip ChromaDB'ye gömer.
- `chat.py`: Sistemin temel zeka ve cevaplama mantığı.
- `app.py`: FastAPI backend ve web sunucusu.
- `templates/`: Modern frontend dosyaları.
- `legacy/`: Geliştirme sürecindeki eski scriptler ve testler.

## ⚠️ Dikkat
Bu proje eğitim amaçlıdır. Veri setinizdeki mesajların gizliliğine dikkat edin; `.env` ve `*.jsonl` dosyalarınızın asla genel paylaşılmadığından emin olun.
