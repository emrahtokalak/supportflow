
Bu proje, LangGraph kütüphanesini kullanarak basit bir AI agent uygulaması geliştirir. Agent, yerel Ollama üzerinde çalışan Gemma3:latest modelini kullanır. Birden fazla alt agent'a yönlendirme, orkestrasyon yapar. 

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

5. **Gemma2 modelinin yüklü olduğunu kontrol edin**
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
python main.py
```
