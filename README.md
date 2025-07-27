# SupportFlow - AI Destekli Müşteri Hizmetleri

Bu proje, LangGraph kütüphanesini kullanarak human-in-the-loop destekli AI agent uygulaması geliştirir. Agent, yerel Ollama üzerinde çalışan Gemma3:latest modelini kullanır. Session tabanlı konuşma yönetimi ile birden fazla alt agent'a yönlendirme ve orkestrasyon yapar.

## Özellikler

- 🤖 **Multi-Agent Sistem**: Faturalama, Tarife/Paket ve Genel Bilgi agent'ları
- 💬 **Session Tabanlı Konuşma**: Müşteri geçmişini koruyan oturum yönetimi
- 🚨 **Human-in-the-Loop**: Otomatik human intervention tespiti
- 🔄 **State Management**: LangGraph ile gelişmiş durum yönetimi
- 🌐 **REST API**: FastAPI tabanlı web servisi
- 📊 **Admin Dashboard**: Session monitoring ve yönetim endpoint'leri

## Gereksinimler

- Python 3.11+
- Ollama
- Gemma3:latest modeli (Ollama üzerinde)

## Kurulum

1. **Projeyi klonlayın veya dosyaları indirin**

2. **Sanal ortamı etkinleştirin** (otomatik olarak oluşturuldu)
   ```bash
   python3.11 -m venv .venv
   source .venv/bin/activate
   ```

3. **Bağımlılıkları yükleyin**
   ```bash
   pip install -r requirements.txt
   ```

4. **Ollama'nın çalıştığından emin olun**
   ```bash
   ollama serve
   ```

5. **Gemma3 modelinin yüklü olduğunu kontrol edin**
   ```bash
   ollama list
   ```
   
   Eğer gemma3:latest yüklü değilse:
   ```bash
   ollama pull gemma3:latest
   ```

## Kullanım

### Komut Satırından Çalıştırma

```bash
python src/supportflow/main.py
```

### API Server Başlatma

```bash
python src/supportflow/api.py
```

API Dokumanı: http://localhost:8000/docs

### Session Tabanlı Chat API Kullanımı

#### 1. Yeni Session Başlatma
```bash
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{
       "message": "Merhaba, fatura bakiyemi öğrenebilir miyim?",
       "customer_info": {
         "name": "Ahmet Yılmaz",
         "phone": "0555 123 4567"
       }
     }'
```

#### 2. Mevcut Session'da Devam Etme
```bash
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{
       "message": "Ödeme planı yapabilir miyiz?",
       "session_id": "YOUR_SESSION_ID"
     }'
```

#### 3. Session Durumu Kontrolü
```bash
curl -X GET "http://localhost:8000/session/YOUR_SESSION_ID/status"
```

#### 4. Human Intervention Gerektiren Session'lar
```bash
curl -X GET "http://localhost:8000/admin/sessions/requiring-human"
```

### Test Scripts

#### API Test Script
```bash
python src/supportflow/test_session_api.py
```

#### Agent Test Script  
```bash
python src/supportflow/test_agent.py
```

## Human-in-the-Loop Özellikleri

### Otomatik Human Intervention

Sistem aşağıdaki durumlarda otomatik olarak human intervention'ı tetikler:

1. **Escalation Keywords**: Müşteri şu kelimeleri kullandığında
   - "şikayet", "müdür", "hukuki", "mahkeme"
   - "iptal", "kapatmak istiyorum", "berbat"
   - "insan", "temsilci", "operatör"

2. **Düşük Güven Skoru**: Agent yanıtının güven skoru %30'un altında olduğunda

### Manuel Escalation

```bash
curl -X POST "http://localhost:8000/session/YOUR_SESSION_ID/escalate" \
     -H "Content-Type: application/json" \
     -d '{
       "reason": "Müşteri manuel olarak human agent talep etti",
       "human_agent_id": "agent_001"
     }'
```

### Session Yönetimi

- **Session Timeout**: 30 dakika inaktiflik sonrası
- **Automatic Cleanup**: Süresi dolmuş session'ların otomatik temizlenmesi
- **Turn History**: Her session'da konuşma geçmişi korunur
- **Metadata Support**: Müşteri bilgileri ve session metadata desteği

## API Endpoints

| Method | Endpoint | Açıklama |
|--------|----------|----------|
| POST | `/chat` | Chat mesajı gönderme |
| GET | `/session/{id}/status` | Session durum bilgisi |
| POST | `/session/{id}/escalate` | Manuel human intervention |
| GET | `/admin/sessions/requiring-human` | Human intervention gerektiren session'lar |
| POST | `/admin/cleanup-sessions` | Expired session temizleme |
| GET | `/health` | Sistem sağlık kontrolü |
| GET | `/docs` | API dokumanı |

## Proje Yapısı

```
src/supportflow/
├── agents/
│   ├── __init__.py
│   ├── router_agent.py      # Ana yönlendirme agent'ı
│   ├── fatura_agent.py      # Faturalama uzmanı
│   └── tarife_agent.py      # Tarife/paket uzmanı
├── session_manager.py       # Session ve human-in-the-loop yönetimi
├── api.py                  # FastAPI web servisi
├── main.py                 # Komut satırı arayüzü
├── test_agent.py           # Agent test scripti
└── test_session_api.py     # API test scripti
```

## Postman Collection

Proje root'unda `postman_collection.json` dosyası bulunmaktadır. Bu dosyayı Postman'e import ederek tüm API endpoint'lerini test edebilirsiniz.

## Geliştirme Notları

- Session'lar bellekte tutulur (production'da Redis/Database önerilir)
- Human intervention logic genişletilebilir
- Agent güven skorları için sentiment analysis eklenebilir
- Webhook support ile external CRM entegrasyonu yapılabilir

## Agent UI

SupportFlow projesi, Türkçe müşteri hizmetleri yetenekleri sunan akıllı AI asistan arayüzü içerir. Agent UI'ın özellikleri:

- **Çoklu Hizmet Desteği**: Faturalandırma sorguları, teknik destek ve genel yardım işlemlerini yönetir
- **Türkçe Dil Arayüzü**: Sorunsuz müşteri etkileşimi için yerel Türkçe dil desteği
- **Etkileşimli Sohbet**: Önerilen eylemlerle gerçek zamanlı konuşma yetenekleri
- **Hizmet Kategorileri**: Faturalandırma, teknik destek ve genel yardım seçeneklerine hızlı erişim

![Agent UI Screenshot](/agent-ui.png)

Arayüz, çeşitli hizmet talepleriyle müşterilere yardımcı olmaya hazır ABCX AI Asistanını göstermekte ve sezgisel, kullanıcı dostu bir deneyim sunmaktadır.
