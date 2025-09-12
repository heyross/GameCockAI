import unittest
from unittest.mock import patch, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import Base, CFTCSwap
from rag import query_swapbot

class TestRag(unittest.TestCase):

    def setUp(self):
        """Set up an in-memory SQLite database for RAG testing."""
        self.engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

        # Monkey-patch the SessionLocal in the rag module
        self.patcher_rag = patch('rag.SessionLocal', self.SessionLocal)
        self.patcher_rag.start()

        # Populate the database with some test data
        db = self.SessionLocal()
        db.add(CFTCSwap(dissemination_id='1', asset_class='Credit', notional_amount=1000000))
        db.add(CFTCSwap(dissemination_id='2', asset_class='Equity', notional_amount=500000))
        db.add(CFTCSwap(dissemination_id='3', asset_class='Rates', notional_amount=2000000))
        db.commit()
        db.close()

    def tearDown(self):
        """Stop the patcher and drop all tables."""
        self.patcher_rag.stop()
        Base.metadata.drop_all(self.engine)

    @patch('rag.ollama.chat')
    def test_query_swapbot_retrieval_and_prompt(self, mock_ollama_chat):
        """Test that SwapBot retrieves correct data and constructs the right prompt."""
        # Mock the response from Ollama
        mock_ollama_chat.return_value = {'message': {'content': 'Mocked response.'}}

        query = "Tell me about Credit swaps"
        response = query_swapbot(query)

        # 1. Verify that Ollama was called
        self.assertTrue(mock_ollama_chat.called)

        # 2. Check the content of the prompt sent to Ollama
        call_args = mock_ollama_chat.call_args
        prompt = call_args[1]['messages'][0]['content']
        
        # Check that the context in the prompt contains data only for 'Credit'
        self.assertIn('Credit', prompt)
        self.assertNotIn('Equity', prompt)
        self.assertNotIn('Rates', prompt)
        self.assertIn('1000000', prompt)

        # 3. Check that the function returns the mocked response
        self.assertEqual(response, 'Mocked response.')

    def test_query_swapbot_no_data(self):
        """Test SwapBot's response when no relevant data is found."""
        query = "Tell me about Forex swaps"
        response = query_swapbot(query)
        self.assertEqual(response, "No relevant data found for your query.")

if __name__ == '__main__':
    unittest.main()
