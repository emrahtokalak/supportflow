#!/usr/bin/env python3
"""
ABCX Müşteri Hizmetleri FastAPI Uygulaması
Router Agent'i kullanarak REST API hizmeti sağlar
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging
import requests
import os
from pathlib import Path

from .agents import RouterAgent
from .session_manager import session_manager

# Logging konfigürasyonu
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI uygulaması
app = FastAPI(
    title="ABCX Müşteri Hizmetleri API",
    description="AI Destekli Müşteri Hizmetleri - Faturalama, Tarife/Paket, Teknik Destek",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Üretimde belirli domainlere sınırlandırın
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files için agentpanel klasörünü mount et
current_dir = Path(__file__).parent.parent.parent  # supportflow root
agentpanel_dir = current_dir / "src/agentpanel"

if agentpanel_dir.exists():
    # Static files'ı root'a mount et ki CSS/JS dosyaları direkt erişilebilir olsun
    app.mount("/src/agentpanel", StaticFiles(directory=str(agentpanel_dir), html=True), name="agentpanel")
    logger.info(f"✅ Static files mounted from: {agentpanel_dir}")
else:
    logger.warning(f"⚠️ AgentPanel directory not found: {agentpanel_dir}")

# Global agent instance
agent: Optional[RouterAgent] = None


class ChatRequest(BaseModel):
    """Chat isteği için model"""
    message: str
    session_id: Optional[str] = None  # Mevcut session devam etmek için
    model: Optional[str] = "gemma3:latest"
    customer_info: Optional[Dict[str, Any]] = None  # Yeni session için müşteri bilgileri


class ChatResponse(BaseModel):
    """Chat yanıtı için model"""
    response: str
    session_id: str
    category: Optional[str] = None
    requires_human: bool = False
    escalation_reason: Optional[str] = None
    turn_count: int = 0
    status: str = "success"


class SessionStatusResponse(BaseModel):
    """Session durumu yanıtı için model"""
    session_id: str
    is_active: bool
    turn_count: int
    requires_human: bool
    escalation_reason: Optional[str] = None
    session_duration_minutes: float
    last_activity: str


class HumanInterventionRequest(BaseModel):
    """Human intervention isteği için model"""
    session_id: str
    reason: str
    human_agent_id: Optional[str] = None


class HealthResponse(BaseModel):
    """Sağlık kontrolü yanıtı için model"""
    status: str
    message: str
    ollama_available: bool


@app.on_event("startup")
async def startup_event():
    """Uygulama başlatılırken çalışır"""
    global agent
    try:
        logger.info("🚀 ABCX Müşteri Hizmetleri API başlatılıyor...")
        agent = RouterAgent("gemma3:latest")
        logger.info("✅ Router Agent başarıyla başlatıldı")
    except Exception as e:
        logger.error(f"❌ Agent başlatma hatası: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Uygulama kapatılırken çalışır"""
    logger.info("👋 ABCX Müşteri Hizmetleri API kapatılıyor...")


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Müşteri chat endpoint'i - Session tabanlı konuşma yönetimi
    
    Args:
        request: Chat isteği (mesaj, session_id, model)
    
    Returns:
        Chat yanıtı ve session bilgileri
    """
    global agent
    
    if not agent:
        raise HTTPException(
            status_code=503,
            detail="Agent henüz başlatılmadı. Lütfen daha sonra tekrar deneyin."
        )
    
    if not request.message.strip():
        raise HTTPException(
            status_code=400,
            detail="Mesaj boş olamaz."
        )
    
    try:
        session_id = request.session_id
        
        if not session_id:
            session_id = session_manager.create_session(request.customer_info)
            logger.info(f"🆕 Yeni session oluşturuldu: {session_id}")
        else:
            session = session_manager.get_session(session_id)
            if not session:
                raise HTTPException(
                    status_code=404,
                    detail=f"Session bulunamadı: {session_id}"
                )
        
        logger.info(f"📞 Session {session_id} - Yeni mesaj: {request.message}")
        
        # Context hazırla
        context = session_manager.get_context_for_agent(session_id)
        
        # Agent'ten yanıt al (conversation history dahil)
        response = agent.chat(request.message, history=context.get("conversation_history", []))
        
        # Session'a turn ekle
        turn_id = session_manager.add_conversation_turn(
            session_id=session_id,
            user_message=request.message,
            agent_response=response,
            category=getattr(agent, 'last_category', None)  # Agent'ten kategori bilgisi
        )
        
        # Güncellenmiş context al
        updated_context = session_manager.get_context_for_agent(session_id)
        
        logger.info(f"✅ Session {session_id} - Yanıt oluşturuldu (Turn: {turn_id})")
        
        return ChatResponse(
            response=response,
            session_id=session_id,
            category=updated_context.get("last_category"),
            requires_human=updated_context.get("requires_human", False),
            escalation_reason=updated_context.get("escalation_reason"),
            turn_count=updated_context.get("turn_count", 0),
            status="success"
        )
        
    except Exception as e:
        logger.error(f"❌ Chat hatası: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Sistem hatası oluştu: {str(e)}"
        )


@app.get("/session/{session_id}/status", response_model=SessionStatusResponse)
async def get_session_status(session_id: str):
    """
    Session durumunu getirir
    
    Args:
        session_id: Session ID
    
    Returns:
        Session durum bilgileri
    """
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=404,
            detail=f"Session bulunamadı: {session_id}"
        )
    
    from datetime import datetime
    duration = (datetime.now() - session.created_at).total_seconds() / 60
    
    return SessionStatusResponse(
        session_id=session_id,
        is_active=session.is_active,
        turn_count=len(session.turns),
        requires_human=session.requires_human_intervention,
        escalation_reason=session.escalation_reason,
        session_duration_minutes=round(duration, 2),
        last_activity=session.last_activity.isoformat()
    )


@app.post("/session/{session_id}/escalate")
async def escalate_to_human(session_id: str, request: HumanInterventionRequest):
    """
    Session'ı human intervention için işaretler
    
    Args:
        session_id: Session ID
        request: Human intervention isteği
    
    Returns:
        İşlem sonucu
    """
    success = session_manager.mark_for_human_intervention(
        session_id=session_id,
        reason=request.reason,
        human_agent_id=request.human_agent_id
    )
    
    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"Session bulunamadı: {session_id}"
        )
    
    return {"status": "success", "message": "Session human intervention için işaretlendi"}


@app.get("/admin/sessions/requiring-human")
async def get_sessions_requiring_human():
    """
    Human intervention gerektiren session'ları listeler
    
    Returns:
        Human intervention gerektiren session listesi
    """
    sessions = session_manager.get_sessions_requiring_human()
    
    result = []
    for session in sessions:
        result.append({
            "session_id": session.session_id,
            "created_at": session.created_at.isoformat(),
            "turn_count": len(session.turns),
            "escalation_reason": session.escalation_reason,
            "customer_info": session.customer_info,
            "last_message": session.turns[-1].user_message if session.turns else None
        })
    
    return {"sessions": result, "count": len(result)}


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Sistem sağlık kontrolü
    
    Returns:
        Sistem durumu ve Ollama bağlantı bilgisi
    """
    try:
        # Ollama bağlantı testi
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        ollama_available = response.status_code == 200
    except Exception:
        ollama_available = False
    
    global agent
    agent_ready = agent is not None
    
    status = "healthy" if agent_ready and ollama_available else "unhealthy"
    
    return HealthResponse(
        status=status,
        message=f"API: {'Ready' if agent_ready else 'Not Ready'}, Ollama: {'Connected' if ollama_available else 'Disconnected'}",
        ollama_available=ollama_available
    )


@app.post("/admin/cleanup-sessions")
async def cleanup_expired_sessions():
    """
    Süresi dolmuş session'ları temizler
    
    Returns:
        Temizlenen session sayısı
    """
    cleaned_count = session_manager.cleanup_expired_sessions()
    return {"cleaned_sessions": cleaned_count, "message": f"{cleaned_count} session temizlendi"}


@app.get("/")
async def serve_index():
    """
    Ana sayfa - Web arayüzünü serve eder
    """
    agentpanel_index = current_dir / "src/agentpanel" / "index.html"
    if agentpanel_index.exists():
        return FileResponse(str(agentpanel_index))
    else:
        return {
            "message": "ABCX Müşteri Hizmetleri API",
            "status": "running",
            "web_interface": "Web arayüzü bulunamadı. agentpanel/index.html dosyasını kontrol edin.",
            "api_docs": "/docs",
            "health": "/health"
        }


@app.get("/styles.css")
async def serve_styles():
    """CSS dosyasını serve eder"""
    css_file = current_dir / "src/agentpanel" / "styles.css"
    if css_file.exists():
        return FileResponse(str(css_file), media_type="text/css")
    else:
        raise HTTPException(status_code=404, detail="CSS file not found")


@app.get("/script.js")
async def serve_script():
    """JavaScript dosyasını serve eder"""
    js_file = current_dir / "src/agentpanel" / "script.js"
    if js_file.exists():
        return FileResponse(str(js_file), media_type="application/javascript")
    else:
        raise HTTPException(status_code=404, detail="JS file not found")


if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 FastAPI sunucusu başlatılıyor...")
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )