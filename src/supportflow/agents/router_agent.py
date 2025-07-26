"""
Ana router agent - müşteri taleplerini doğru departmanlara yönlendirir
"""

import operator
from typing import Annotated, Any, Dict, List, TypedDict

from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import OllamaLLM
from langgraph.graph import END, StateGraph

from .fatura_agent import FaturaAgent
from .tarife_agent import TarifeAgent


class AgentState(TypedDict):
    """Agent state'ini tanımlayan sınıf"""

    messages: Annotated[List[str], operator.add]
    user_input: str
    response: str
    step_count: int
    category: str  # Tespit edilen kategori


class RouterAgent:
    """Telekomünikasyon şirketi müşteri hizmetleri router agent sınıfı"""

    def __init__(self, model_name: str = "gemma3:latest"):
        """
        Agent'i başlatır

        Args:
            model_name: Ollama'da kullanılacak model adı
        """
        self.llm = OllamaLLM(model=model_name, base_url="http://localhost:11434")

        # Fatura Agent'ini başlat
        self.fatura_agent = FaturaAgent(model_name)

        # Tarife Agent'ini başlat
        self.tarife_agent = TarifeAgent(model_name)

        # Telekomünikasyon müşteri hizmetleri kategorileri
        self.categories = {
            "faturalama": ["fatura", "borç", "ödeme", "tahsilat", "bakiye", "hesap"],
            "paket_tarife": [
                "paket",
                "tarife",
                "hat",
                "internet",
                "konuşma",
                "sms",
                "gb",
                "kampanya",
                "kontör",
                "dakika",
                "fiber",
                "adsl",
                "mobil",
                "değişim",
                "seçim",
            ],
            "teknik_destek": [
                "internet",
                "bağlantı",
                "hız",
                "modem",
                "router",
                "arıza",
                "kesinti",
            ],
            "genel_bilgi": [
                "şirket",
                "mağaza",
                "adres",
                "iletişim",
                "çalışma saatleri",
                "şube",
            ],
        }

        # Agent'in kişiliğini tanımlayan prompt
        self.prompt = ChatPromptTemplate.from_template(
            """Sen bir telekomünikasyon şirketi müşteri hizmetleri temsilcisisin. 
            Müşterilerinizle güler yüzlü, yardımcı ve profesyonel bir şekilde konuş.
            
            Müşteri kategorileri:
            1. FATURALAMA: Fatura, ödeme, borç, tahsilat konuları
            2. PAKET/TARİFE: Hat, internet paketleri, tarife değişikliği, kampanyalar
            3. TEKNİK DESTEK: İnternet bağlantı sorunları, hız problemleri, modem/router sorunları
            4. GENEL BİLGİ: Şirket bilgileri, mağaza adresleri, çalışma saatleri
            
            Görevin:
            1. Müşteriyi sıcak bir şekilde karşıla
            2. Sorunu hangi kategoriye girdiğini belirle
            3. İlgili departmana yönlendirme yap
            4. Kısa ve yararlı bilgi ver
            
            Müşteri sorusu: {user_input}
            
            Yanıt:"""
        )

        # Graph'i oluştur
        self.graph = self._create_graph()

    def _create_graph(self) -> StateGraph:
        """Langgraph state graph'ini oluşturur"""

        def analyze_request(state: AgentState) -> AgentState:
            """Müşteri talebini analiz eder ve kategorize eder"""
            print(f"🔄 Adım {state['step_count']}: Müşteri talebi analiz ediliyor...")

            user_input_lower = state["user_input"].lower()
            detected_category = "genel_bilgi"  # varsayılan kategori

            # Kategori tespiti, burası vektörel olmalı.
            for category, keywords in self.categories.items():
                if any(keyword in user_input_lower for keyword in keywords):
                    detected_category = category
                    break

            state["messages"].append(f"Müşteri: {state['user_input']}")
            state["messages"].append(f"Tespit edilen kategori: {detected_category}")
            state["category"] = detected_category
            state["step_count"] += 1
            return state

        def route_customer(state: AgentState) -> AgentState:
            """Müşteriyi doğru departmana yönlendirir"""
            print(f"🎯 Adım {state['step_count']}: Müşteri yönlendiriliyor...")

            # Kategori kontrolü - İlgili agent'lara yönlendir
            if state["category"] == "faturalama":
                print("💳 Faturalama departmanına yönlendiriliyor...")
                response = self.fatura_agent.handle_billing_request(state["user_input"])
                state["response"] = response
                state["messages"].append(f"Faturalama Uzmanı: {response}")
            elif state["category"] == "paket_tarife":
                print("📦 Tarife ve Paket departmanına yönlendiriliyor...")
                response = self.tarife_agent.handle_tarife_request(state["user_input"])
                state["response"] = response
                state["messages"].append(f"Tarife Uzmanı: {response}")
            else:
                # Diğer kategoriler için genel router yanıtı
                formatted_prompt = self.prompt.format(user_input=state["user_input"])
                response = self.llm.invoke(formatted_prompt)
                state["response"] = response
                state["messages"].append(f"Müşteri Temsilcisi: {response}")

            state["step_count"] += 1
            return state

        def provide_service(state: AgentState) -> AgentState:
            """Müşteriye hizmet sağlar ve süreci tamamlar"""
            print(f"✅ Adım {state['step_count']}: Müşteri hizmeti tamamlanıyor...")
            print(f"📞 Müşteri yönlendirmesi tamamlandı")
            return state

        # Graph'i oluştur
        workflow = StateGraph(AgentState)

        # Node'ları ekle
        workflow.add_node("analyze_request", analyze_request)
        workflow.add_node("route_customer", route_customer)
        workflow.add_node("provide_service", provide_service)

        # Edge'leri ekle
        workflow.set_entry_point("analyze_request")
        workflow.add_edge("analyze_request", "route_customer")
        workflow.add_edge("route_customer", "provide_service")
        workflow.add_edge("provide_service", END)

        return workflow.compile()

    def chat(self, user_input: str) -> str:
        """
        Müşteri ile sohbet eder ve doğru departmana yönlendirir

        Args:
            user_input: Müşterinin talebi

        Returns:
            Müşteri temsilcisinin yanıtı
        """
        print(f"\n📞 Yeni müşteri araması...")
        print(f"👤 Müşteri: {user_input}")
        print("-" * 50)

        # Initial state
        initial_state = AgentState(
            messages=[], user_input=user_input, response="", step_count=1, category=""
        )

        # Graph'i çalıştır
        result = self.graph.invoke(initial_state)

        return result["response"]
