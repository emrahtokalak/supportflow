#!/usr/bin/env python3
"""
ABCX Müşteri Hizmetleri Uygulaması
Ana giriş noktası - Router Agent'i kullanarak müşteri taleplerini işler
CLI ve API modlarını destekler
"""

import sys
import argparse
from agents import RouterAgent


def run_cli():
    """CLI modunda çalıştır"""
    print("📞 ABCX Müşteri Hizmetleri'ne Hoş Geldiniz!")
    print("🤖 AI Destekli Müşteri Temsilcisi")
    print("💡 Faturalama, Tarife/Paket, Teknik Destek için yardıma hazırım")
    print("⌨️  'quit' yazarak çıkabilirsiniz\n")

    try:
        # Router Agent'i başlat
        agent = RouterAgent("gemma3:latest")

        # Ana döngü
        while True:
            user_input = input("\n👤 Siz: ").strip()

            if user_input.lower() in ["quit", "exit", "çık", "çıkış"]:
                print("👋 ABCX'ü tercih ettiğiniz için teşekkürler!")
                break

            if not user_input:
                print("❌ Lütfen talebinizi yazın.")
                continue

            try:
                response = agent.chat(user_input)
                print(f"\n🎧 Müşteri Temsilcisi: {response}")

            except Exception as e:
                print(f"❌ Sistem hatası oluştu: {e}")
                print("💡 Ollama servisinin çalıştığından emin olun: ollama serve")

    except KeyboardInterrupt:
        print("\n\n👋 Görüşme sonlandırıldı. İyi günler!")
    except Exception as e:
        print(f"❌ Kritik sistem hatası: {e}")


def run_api():
    """API modunda çalıştır"""
    try:
        import uvicorn
        from api import app
        
        print("🚀 ABCX Müşteri Hizmetleri API başlatılıyor...")
        print("📖 API Dokümantasyonu: http://localhost:8000/docs")
        print("🔍 ReDoc: http://localhost:8000/redoc")
        print("⚡ API URL: http://localhost:8000")
        print("🛑 CTRL+C ile durdurun\n")
        
        uvicorn.run(
            "api:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except ImportError:
        print("❌ FastAPI ve Uvicorn kurulu değil!")
        print("💡 Yüklemek için: pip install fastapi uvicorn")
        sys.exit(1)
    except Exception as e:
        print(f"❌ API başlatma hatası: {e}")
        sys.exit(1)


def main():
    """Ana fonksiyon - CLI argümanlarını parse eder"""
    parser = argparse.ArgumentParser(
        description="ABCX Müşteri Hizmetleri - AI Destekli Müşteri Temsilcisi",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Kullanım Örnekleri:
  python main.py              # CLI modunda çalıştır
  python main.py --cli         # CLI modunda çalıştır (açık)
  python main.py --api         # API sunucusunu başlat
  python main.py --help        # Bu yardım mesajını göster

API Endpoints:
  GET  /                       # Ana sayfa
  GET  /health                 # Sistem durumu
  POST /chat                   # Chat endpoint'i
  GET  /docs                   # API dokümantasyonu
        """
    )
    
    parser.add_argument(
        "--api",
        action="store_true",
        help="API sunucusunu başlat (http://localhost:8000)"
    )
    
    parser.add_argument(
        "--cli",
        action="store_true",
        help="CLI modunda çalıştır (varsayılan)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="API sunucusu için port numarası (varsayılan: 8000)"
    )
    
    args = parser.parse_args()
    
    # Mod belirleme
    if args.api:
        run_api()
    else:
        # Varsayılan olarak CLI modunda çalıştır
        run_cli()


if __name__ == "__main__":
    main()
