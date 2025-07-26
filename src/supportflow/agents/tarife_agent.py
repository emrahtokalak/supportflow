"""
Tarife, kontör ve paket işlemleri için özel agent
"""

from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate


class TarifeAgent:
    """Tarife, kontör ve paket işlemleri için özel agent sınıfı"""
    
    def __init__(self, model_name: str = "gemma3:latest"):
        """
        Tarife Agent'i başlatır
        
        Args:
            model_name: Ollama'da kullanılacak model adı
        """
        self.llm = OllamaLLM(
            model=model_name,
            base_url="http://localhost:11434"
        )
        
        # Tarife ve paket konularına özel prompt
        self.prompt = ChatPromptTemplate.from_template(
            """Sen TelekomTürk'ün tarife ve paket departmanından bir uzmansın. 
            Müşterilerin tarife değişikliği, paket seçimi, kontör işlemleri konularında yardımcı oluyorsun.
            
            Hizmetlerin:
            - Tarife seçimi ve değişikliği
            - İnternet paketleri (Fiber, ADSL, Mobil)
            - Konuşma dakikaları ve SMS paketleri
            - Kontör yükleme işlemleri
            - Kampanya ve indirimler
            - Paket kullanım sorguları
            - Hat açma/kapatma işlemleri
            
            Müşteriye ihtiyaçlarına uygun paketleri öner.
            Fiyat ve özellik karşılaştırmaları yap.
            Adım adım paket değişim sürecini anlat.
            
            Müşteri talebi: {user_input}
            
            Tarife Uzmanı Yanıtı:"""
        )
    
    def handle_tarife_request(self, user_input: str) -> str:
        """
        Tarife ve paket talebini işler
        
        Args:
            user_input: Müşterinin tarife/paket talebi
            
        Returns:
            Tarife uzmanının yanıtı
        """
        print(f"📦 Tarife ve Paket Departmanı: Talep işleniyor...")
        
        # Prompt'u hazırla ve LLM'e gönder
        formatted_prompt = self.prompt.format(user_input=user_input)
        response = self.llm.invoke(formatted_prompt)
        
        return response
