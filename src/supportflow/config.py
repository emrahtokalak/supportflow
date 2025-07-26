"""
Langgraph Agent konfigürasyon dosyası
"""

# Ollama ayarları
OLLAMA_CONFIG = {
    "base_url": "http://localhost:11434",
    "model_name": "gemma3:latest",
    "timeout": 30
}

# Agent ayarları
AGENT_CONFIG = {
    "max_steps": 10,
    "verbose": True,
    "temperature": 0.7
}

# Prompt şablonları
PROMPTS = {
    "default": """Sen yardımcı ve bilgili bir AI asistanısın. 
    Kullanıcının sorularını mümkün olduğunca net ve faydalı şekilde yanıtla.
    
    Kullanıcı sorusu: {user_input}
    
    Yanıt:""",
    
    "creative": """Sen yaratıcı ve eğlenceli bir AI asistanısın.
    Sorulara yaratıcı ve ilginç yaklaşımlarla yanıt ver.
    
    Kullanıcı sorusu: {user_input}
    
    Yaratıcı yanıt:""",
    
    "technical": """Sen teknik bir uzman AI asistanısın.
    Sorulara detaylı ve teknik açıklamalarla yanıt ver.
    
    Kullanıcı sorusu: {user_input}
    
    Teknik yanıt:"""
}
