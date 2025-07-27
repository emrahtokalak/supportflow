"""
Tarife, kontör ve paket işlemleri için özel agent
"""

from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from typing import List


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
            """Sen ABCX'ün tarife ve paket departmanından bir uzmansın. 
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
    
    def handle_tarife_request(self, user_input: str, history: List[str] = None) -> str:
        """
        Tarife ve paket ile ilgili müşteri taleplerini işler

        Args:
            user_input: Müşterinin tarife talebi
            history: Önceki konuşma geçmişi

        Returns:
            Tarife uzmanının yanıtı
        """
        print(f"📦 Tarife Agent: '{user_input}' talebi işleniyor...")

        # Konuşma geçmişini formatla
        conversation_context = ""
        if history:
            conversation_context = "\n".join([f"- {msg}" for msg in history[-5:]])  # Son 5 mesaj
            conversation_context = f"\n\nÖnceki konuşma:\n{conversation_context}\n"

        # Prompt'u güncelle
        updated_prompt = ChatPromptTemplate.from_template(
            """Sen bir telekomünikasyon şirketi tarife ve paket uzmanısın.
            Müşterilerinizle güler yüzlü, anlayışlı ve bilgili bir şekilde konuş.
            
            Uzmanlık alanların:
            - İnternet paketleri (Fiber, ADSL, Mobil)
            - Konuşma tarifeleri ve dakika paketleri
            - SMS paketleri
            - Kampanya ve promosyonlar
            - Hat açma/kapama işlemleri
            - Tarife değişiklikleri
            - Kontör yükleme
            
            Görevlerin:
            1. Müşterinin ihtiyacını anlayıp en uygun paketi öner
            2. Mevcut paket bilgilerini net bir şekilde açıkla
            3. Kampanya ve avantajları detaylı anlat
            4. Müşteriyi tatmin edici çözümler sun{conversation_context}
            
            Müşteri talebi: {user_input}
            
            Tarife Uzmanı Yanıtı:"""
        )
        
        formatted_prompt = updated_prompt.format(
            user_input=user_input,
            conversation_context=conversation_context
        )
        response = self.llm.invoke(formatted_prompt)
        
        print(f"📦 Tarife Agent yanıtı: {response[:100]}...")
        return response
