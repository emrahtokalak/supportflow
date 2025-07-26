#!/usr/bin/env python3
"""
Langgraph Agent için test dosyası
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Ana dizini Python path'ine ekle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import SimpleAgent, AgentState


class TestSimpleAgent(unittest.TestCase):
    """SimpleAgent sınıfı için test cases"""
    
    def setUp(self):
        """Her test öncesi çalışır"""
        self.mock_llm_patcher = patch('main.OllamaLLM')
        self.mock_llm_class = self.mock_llm_patcher.start()
        self.mock_llm_instance = MagicMock()
        self.mock_llm_class.return_value = self.mock_llm_instance
        
        self.agent = SimpleAgent("gemma3")
    
    def tearDown(self):
        """Her test sonrası çalışır"""
        self.mock_llm_patcher.stop()
    
    def test_agent_initialization(self):
        """Agent'in doğru şekilde başlatıldığını test eder"""
        self.assertIsNotNone(self.agent.llm)
        self.assertIsNotNone(self.agent.prompt)
        self.assertIsNotNone(self.agent.graph)
    
    def test_chat_method(self):
        """Chat metodunun çalıştığını test eder"""
        # Mock LLM response
        self.mock_llm_instance.invoke.return_value = "Test yanıtı"
        
        # Test chat
        response = self.agent.chat("Merhaba")
        
        # Assertions
        self.assertEqual(response, "Test yanıtı")
        self.mock_llm_instance.invoke.assert_called_once()
    
    def test_agent_state_structure(self):
        """AgentState yapısını test eder"""
        state = AgentState(
            messages=[],
            user_input="test",
            response="",
            step_count=1
        )
        
        self.assertEqual(state["user_input"], "test")
        self.assertEqual(state["step_count"], 1)
        self.assertEqual(len(state["messages"]), 0)


class TestIntegration(unittest.TestCase):
    """Entegrasyon testleri"""
    
    @patch('main.OllamaLLM')
    def test_full_workflow(self, mock_llm_class):
        """Tam workflow'u test eder"""
        # Mock setup
        mock_llm_instance = MagicMock()
        mock_llm_instance.invoke.return_value = "Mock yanıt"
        mock_llm_class.return_value = mock_llm_instance
        
        # Agent oluştur
        agent = SimpleAgent("gemma3")
        
        # Chat test et
        response = agent.chat("Test sorusu")
        
        # Verify
        self.assertEqual(response, "Mock yanıt")
        mock_llm_instance.invoke.assert_called_once()


if __name__ == '__main__':
    # Test suite'i çalıştır
    unittest.main(verbosity=2)
