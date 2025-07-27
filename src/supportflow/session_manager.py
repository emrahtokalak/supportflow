"""
Session Management for Human-in-the-Loop Chat System
Maintains conversation state and enables human intervention capabilities
"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import threading
import json


@dataclass
class ConversationTurn:
    """Tek bir konuşma turunu temsil eder"""
    id: str
    timestamp: datetime
    user_message: str
    agent_response: str
    category: Optional[str] = None
    agent_type: Optional[str] = None
    confidence: Optional[float] = None
    requires_human: bool = False
    human_notes: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConversationSession:
    """Bir müşteri oturumunu temsil eder"""
    session_id: str
    created_at: datetime
    last_activity: datetime
    turns: List[ConversationTurn] = field(default_factory=list)
    customer_info: Dict[str, Any] = field(default_factory=dict)
    session_metadata: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True
    requires_human_intervention: bool = False
    human_agent_id: Optional[str] = None
    escalation_reason: Optional[str] = None


class SessionManager:
    """Session yönetimi ve human-in-the-loop fonksiyonları"""
    
    def __init__(self, session_timeout_minutes: int = 30):
        """
        Session Manager'ı başlatır
        
        Args:
            session_timeout_minutes: Session timeout süresi (dakika)
        """
        self.sessions: Dict[str, ConversationSession] = {}
        self.session_timeout = timedelta(minutes=session_timeout_minutes)
        self._lock = threading.RLock()
        
        # Human intervention triggers
        self.escalation_keywords = [
            "şikayet", "çok kötü", "müdür", "hukuki", "mahkeme", 
            "iptal", "kapatmak istiyorum", "berbat", "rezalet",
            "memnun değilim", "insan", "temsilci", "operatör"
        ]
        
        # Low confidence threshold for human intervention
        self.low_confidence_threshold = 0.3
    
    def create_session(self, customer_info: Dict[str, Any] = None) -> str:
        """
        Yeni bir session oluşturur
        
        Args:
            customer_info: Müşteri bilgileri
            
        Returns:
            Session ID
        """
        session_id = str(uuid.uuid4())
        now = datetime.now()
        
        with self._lock:
            self.sessions[session_id] = ConversationSession(
                session_id=session_id,
                created_at=now,
                last_activity=now,
                customer_info=customer_info or {}
            )
        
        print(f"🆕 Yeni session oluşturuldu: {session_id}")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[ConversationSession]:
        """
        Session'ı getirir
        
        Args:
            session_id: Session ID
            
        Returns:
            ConversationSession veya None
        """
        with self._lock:
            session = self.sessions.get(session_id)
            if session and self._is_session_expired(session):
                self._cleanup_session(session_id)
                return None
            return session
    
    def add_conversation_turn(
        self, 
        session_id: str, 
        user_message: str, 
        agent_response: str,
        category: str = None,
        agent_type: str = None,
        confidence: float = None
    ) -> str:
        """
        Session'a yeni bir konuşma turu ekler
        
        Args:
            session_id: Session ID
            user_message: Kullanıcı mesajı
            agent_response: Agent yanıtı
            category: Tespit edilen kategori
            agent_type: Kullanılan agent türü
            confidence: Yanıt güven skoru
            
        Returns:
            Turn ID
        """
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session bulunamadı: {session_id}")
        
        turn_id = str(uuid.uuid4())
        now = datetime.now()
        
        # Human intervention gerekip gerekmediğini kontrol et
        requires_human = self._should_escalate_to_human(
            user_message, agent_response, confidence
        )
        
        turn = ConversationTurn(
            id=turn_id,
            timestamp=now,
            user_message=user_message,
            agent_response=agent_response,
            category=category,
            agent_type=agent_type,
            confidence=confidence,
            requires_human=requires_human
        )
        
        with self._lock:
            session.turns.append(turn)
            session.last_activity = now
            
            # Session seviyesinde human intervention işaretle
            if requires_human:
                session.requires_human_intervention = True
                if confidence and confidence < self.low_confidence_threshold:
                    session.escalation_reason = "Düşük güven skoru"
                elif self._contains_escalation_keywords(user_message):
                    session.escalation_reason = "Müşteri escalation talep etti"
        
        print(f"🔄 Turn eklendi - Session: {session_id}, Turn: {turn_id}, Human: {requires_human}")
        return turn_id
    
    def get_conversation_history(self, session_id: str, last_n_turns: int = 10) -> List[str]:
        """
        Session'ın konuşma geçmişini getirir
        
        Args:
            session_id: Session ID
            last_n_turns: Son kaç turn'ü getir
            
        Returns:
            Konuşma geçmişi listesi
        """
        session = self.get_session(session_id)
        if not session:
            return []
        
        history = []
        for turn in session.turns[-last_n_turns:]:
            history.append(f"Müşteri: {turn.user_message}")
            history.append(f"Sistem: {turn.agent_response}")
        
        return history
    
    def get_context_for_agent(self, session_id: str) -> Dict[str, Any]:
        """
        Agent için context bilgilerini hazırlar
        
        Args:
            session_id: Session ID
            
        Returns:
            Context dictionary
        """
        session = self.get_session(session_id)
        if not session:
            return {}
        
        return {
            "session_id": session_id,
            "conversation_history": self.get_conversation_history(session_id, 5),
            "customer_info": session.customer_info,
            "session_duration": (datetime.now() - session.created_at).total_seconds() / 60,
            "turn_count": len(session.turns),
            "requires_human": session.requires_human_intervention,
            "escalation_reason": session.escalation_reason,
            "last_category": session.turns[-1].category if session.turns else None
        }
    
    def mark_for_human_intervention(
        self, 
        session_id: str, 
        reason: str, 
        human_agent_id: str = None
    ) -> bool:
        """
        Session'ı human intervention için işaretler
        
        Args:
            session_id: Session ID
            reason: Escalation sebebi
            human_agent_id: Human agent ID
            
        Returns:
            İşlem başarılı mı
        """
        session = self.get_session(session_id)
        if not session:
            return False
        
        with self._lock:
            session.requires_human_intervention = True
            session.escalation_reason = reason
            session.human_agent_id = human_agent_id
        
        print(f"🚨 Human intervention - Session: {session_id}, Reason: {reason}")
        return True
    
    def get_sessions_requiring_human(self) -> List[ConversationSession]:
        """
        Human intervention gerektiren session'ları getirir
        
        Returns:
            Human intervention gerektiren session listesi
        """
        with self._lock:
            return [
                session for session in self.sessions.values()
                if session.requires_human_intervention and session.is_active
            ]
    
    def cleanup_expired_sessions(self) -> int:
        """
        Süresi dolmuş session'ları temizler
        
        Returns:
            Temizlenen session sayısı
        """
        expired_sessions = []
        
        with self._lock:
            for session_id, session in self.sessions.items():
                if self._is_session_expired(session):
                    expired_sessions.append(session_id)
            
            for session_id in expired_sessions:
                self._cleanup_session(session_id)
        
        if expired_sessions:
            print(f"🧹 {len(expired_sessions)} expired session temizlendi")
        
        return len(expired_sessions)
    
    def _should_escalate_to_human(
        self, 
        user_message: str, 
        agent_response: str, 
        confidence: float = None
    ) -> bool:
        """
        Human intervention gerekip gerekmediğini kontrol eder
        """
        # Düşük güven skoru kontrolü
        if confidence and confidence < self.low_confidence_threshold:
            return True
        
        # Escalation keyword kontrolü
        if self._contains_escalation_keywords(user_message):
            return True
        
        return False
    
    def _contains_escalation_keywords(self, message: str) -> bool:
        """Escalation keyword'leri kontrol eder"""
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in self.escalation_keywords)
    
    def _is_session_expired(self, session: ConversationSession) -> bool:
        """Session'ın süresi dolmuş mu kontrol eder"""
        return datetime.now() - session.last_activity > self.session_timeout
    
    def _cleanup_session(self, session_id: str):
        """Session'ı temizler"""
        if session_id in self.sessions:
            self.sessions[session_id].is_active = False
            # İsteğe bağlı: Session'ı tamamen sil veya archive et
            # del self.sessions[session_id]


# Global session manager instance
session_manager = SessionManager()
