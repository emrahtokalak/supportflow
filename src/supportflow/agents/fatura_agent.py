"""
Faturalama ve ödeme işlemleri için özel agent
"""

from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate


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
            """Sen TelekomTürk'ün faturalama departmanından bir uzmansın. 
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
    
    def handle_billing_request(self, user_input: str) -> str:
        """
        Faturalama talebini işler
        
        Args:
            user_input: Müşterinin faturalama talebi
            
        Returns:
            Faturalama uzmanının yanıtı
        """
        print(f"💳 Faturalama Departmanı: Talep işleniyor...")
        
        # Prompt'u hazırla ve LLM'e gönder
        formatted_prompt = self.prompt.format(user_input=user_input)
        response = self.llm.invoke(formatted_prompt)
        
        return response
