#!/usr/bin/env python3
"""
Session-based API test script
Human-in-the-loop özelliklerini test eder
"""

import requests
import json
import time


def test_session_based_chat():
    """Session tabanlı chat API'sını test eder"""
    
    base_url = "http://localhost:8000"
    
    print("🧪 Session-based Chat API Test Başlıyor...")
    print("=" * 60)
    
    # 1. Sağlık kontrolü
    print("\n1️⃣  Sağlık Kontrolü")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            health_data = response.json()
            print(f"System Status: {health_data['status']}")
            print(f"Message: {health_data['message']}")
        else:
            print("❌ API çalışmıyor!")
            return
    except Exception as e:
        print(f"❌ Bağlantı hatası: {e}")
        return
    
    # 2. İlk mesaj - yeni session
    print("\n2️⃣  Yeni Session Başlatma")
    chat_data = {
        "message": "Merhaba, fatura bakiyemi öğrenebilir miyim?",
        "customer_info": {
            "name": "Ahmet Yılmaz",
            "phone": "0555 123 4567"
        }
    }
    
    response = requests.post(f"{base_url}/chat", json=chat_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        chat_response = response.json()
        session_id = chat_response["session_id"]
        print(f"✅ Session ID: {session_id}")
        print(f"📋 Category: {chat_response.get('category', 'N/A')}")
        print(f"🤖 Response: {chat_response['response'][:100]}...")
        print(f"🚨 Requires Human: {chat_response.get('requires_human', False)}")
    else:
        print(f"❌ Chat hatası: {response.text}")
        return
    
    # 3. Session devam ettirme
    print("\n3️⃣  Session Devam Ettirme")
    chat_data = {
        "message": "Ödeme planı yapabilir miyiz?",
        "session_id": session_id
    }
    
    response = requests.post(f"{base_url}/chat", json=chat_data)
    if response.status_code == 200:
        chat_response = response.json()
        print(f"✅ Turn Count: {chat_response.get('turn_count', 0)}")
        print(f"🤖 Response: {chat_response['response'][:100]}...")
    
    # 4. Session durumu
    print("\n4️⃣  Session Durumu Kontrolü")
    response = requests.get(f"{base_url}/session/{session_id}/status")
    if response.status_code == 200:
        status_data = response.json()
        print(f"✅ Session Active: {status_data['is_active']}")
        print(f"📊 Turn Count: {status_data['turn_count']}")
        print(f"⏱️  Duration: {status_data['session_duration_minutes']:.2f} minutes")
        print(f"🚨 Requires Human: {status_data['requires_human']}")
    
    # 5. Human intervention trigger test
    print("\n5️⃣  Human Intervention Test")
    chat_data = {
        "message": "Bu çok kötü bir hizmet! Müdürle konuşmak istiyorum!",
        "session_id": session_id
    }
    
    response = requests.post(f"{base_url}/chat", json=chat_data)
    if response.status_code == 200:
        chat_response = response.json()
        print(f"🚨 Requires Human: {chat_response.get('requires_human', False)}")
        print(f"📝 Escalation Reason: {chat_response.get('escalation_reason', 'N/A')}")
        
        if chat_response.get('requires_human'):
            print("✅ Human intervention başarıyla tetiklendi!")
    
    # 6. Human intervention gerektiren session'ları listele
    print("\n6️⃣  Human Intervention Gerektiren Session'lar")
    response = requests.get(f"{base_url}/admin/sessions/requiring-human")
    if response.status_code == 200:
        sessions_data = response.json()
        print(f"📋 Count: {sessions_data['count']}")
        for session in sessions_data['sessions']:
            print(f"  - Session: {session['session_id'][:8]}...")
            print(f"    Reason: {session['escalation_reason']}")
            print(f"    Turns: {session['turn_count']}")
    
    # 7. Manuel escalation
    print("\n7️⃣  Manuel Escalation Test")
    escalation_data = {
        "reason": "Müşteri manuel olarak human agent talep etti",
        "human_agent_id": "agent_001"
    }
    
    response = requests.post(f"{base_url}/session/{session_id}/escalate", json=escalation_data)
    if response.status_code == 200:
        print("✅ Manuel escalation başarılı!")
        print(f"📝 Response: {response.json()['message']}")
    
    print("\n" + "=" * 60)
    print("🎉 Test Tamamlandı!")


if __name__ == "__main__":
    test_session_based_chat()
