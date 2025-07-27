"""
Faturalama ve ödeme işlemleri için özel agent
"""

from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from typing import List


class FaturaAgent:
    """Faturalama ve ödeme işlemleri için özel agent sınıfı"""
    
    def __init__(self, model_name: str = "gemma3:latest"):
        """
        Fatura Agent'i başlatır
        
        Args:
            model_name: Ollama'da kullanılacak model adı
        """
        self.llm = OllamaLLM(
            model=model_name,
            base_url="http://localhost:11434"
        )
        
        # Faturalama konularına özel prompt
        self.prompt = ChatPromptTemplate.from_template(
            """Sen ABCX'ün faturalama departmanından bir uzmansın. 
            Müşterilerin fatura, ödeme, borç ve bakiye konularında yardımcı oluyorsun.
            
            Hizmetlerin:
            - Fatura sorgulama ve detayları
            - Ödeme yöntemleri ve planları
            - Borç yapılandırma
            - Bakiye sorguları
            - Tahsilat süreçleri
            - Fatura itirazları
            
            Müşteriye profesyonel, anlayışlı ve çözüm odaklı yaklaş.
            Gerekirse adım adım yönlendirme yap.
            
            Müşteri talebi: {user_input}
            
            Faturalama Uzmanı Yanıtı:"""
        )
    
    def handle_billing_request(self, user_input: str, history: List[str] = None) -> str:
        """
        Fatura ile ilgili müşteri taleplerini işler

        Args:
            user_input: Müşterinin fatura talebi
            history: Önceki konuşma geçmişi

        Returns:
            Fatura uzmanının yanıtı
        """
        print(f"💳 Fatura Agent: '{user_input}' talebi işleniyor...")

        # Konuşma geçmişini formatla
        conversation_context = ""
        if history:
            conversation_context = "\n".join([f"- {msg}" for msg in history[-5:]])  # Son 5 mesaj
            conversation_context = f"\n\nÖnceki konuşma:\n{conversation_context}\n"

        # Prompt'u güncelle
        updated_prompt = ChatPromptTemplate.from_template(
            """Sen bir telekomünikasyon şirketi faturalama uzmanısın. 
            Müşterilerinizle profesyonel, yardımcı ve sabırlı bir şekilde konuş.
            
            Uzmanlık alanların:
            - Fatura sorgulama ve açıklama
            - Ödeme planları ve taksitlendirme
            - Borç yapılandırma
            - Fatura itirazları
            - Ödeme yöntemleri
            - Bakiye sorgulama
            
            Görevlerin:
            1. Müşterinin fatura sorununu anlayıp çöz
            2. Gerekirse ödeme seçenekleri sun
            3. Net ve anlaşılır bilgi ver
            4. Müşteriyi memnun et{conversation_context}
            
            Müşteri talebi: {user_input}
            
            Faturalama Uzmanı Yanıtı:"""
        )
        
        formatted_prompt = updated_prompt.format(
            user_input=user_input,
            conversation_context=conversation_context
        )
        response = self.llm.invoke(formatted_prompt)
        
        print(f"💳 Fatura Agent yanıtı: {response[:100]}...")
        return response
