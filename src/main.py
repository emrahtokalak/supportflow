#!/usr/bin/env python3
"""
Telekomünikasyon Şirketi Müşteri Hizmetleri Uygulaması
Ana giriş noktası - Router Agent'i kullanarak müşteri taleplerini işler
"""

from agents import RouterAgent


def main():
    """Ana fonksiyon"""
    print("📞 TelekomTürk Müşteri Hizmetleri'ne Hoş Geldiniz!")
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
                print("👋 TelekomTürk'ü tercih ettiğiniz için teşekkürler!")
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


if __name__ == "__main__":
    main()
