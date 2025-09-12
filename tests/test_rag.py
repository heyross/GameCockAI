import unittest
import json
from unittest.mock import patch, MagicMock

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Assuming TOOL_MAP is imported in rag.py and we need to patch it there
from rag import query_swapbot, TOOL_MAP

class TestAgenticRag(unittest.TestCase):

    @patch('rag.ollama.chat')
    def test_ai_uses_search_tool(self, mock_ollama_chat):
        """Test that the AI correctly decides to use the search_companies tool."""
        # --- Setup Mocks ---
        # 1. Mock the tool function that will be called.
        mock_search_function = MagicMock(return_value=json.dumps([{'title': 'Apple Inc.', 'ticker': 'AAPL'}]))

        # 2. Patch the TOOL_MAP dictionary in the 'rag' module to use the mock function.
        with patch.dict(TOOL_MAP, {'search_companies': {'function': mock_search_function, 'schema': {}}}):
            
            # 3. AI's first response: Decide to use the 'search_companies' tool.
            mock_ollama_chat.side_effect = [
                {
                    'message': {
                        'role': 'assistant',
                        'tool_calls': [{
                            'function': {
                                'name': 'search_companies',
                                'arguments': {'company_name': 'apple'}
                            }
                        }]
                    }
                },
                # 4. AI's second response: Formulate a final answer based on the tool's output.
                {
                    'message': {
                        'role': 'assistant',
                        'content': 'I found a company called Apple Inc.'
                    }
                }
            ]

            # --- Run Test ---
            messages = []
            response = query_swapbot("find apple", messages)

            # --- Assertions ---
            # Verify that our mock tool was called with the correct arguments.
            mock_search_function.assert_called_once_with(company_name='apple')

            # Verify that the final response is what we expect.
            self.assertEqual(response, 'I found a company called Apple Inc.')

            # Verify that the conversation history is correctly maintained.
            self.assertEqual(len(messages), 4) # User -> AI (tool) -> Tool -> AI (final)
            self.assertEqual(messages[0]['role'], 'user')
            self.assertEqual(messages[1]['role'], 'assistant')
            self.assertIsNotNone(messages[1].get('tool_calls'))
            self.assertEqual(messages[2]['role'], 'tool')
            self.assertEqual(messages[3]['role'], 'assistant')

    @patch('rag.ollama.chat')
    def test_ai_answers_directly(self, mock_ollama_chat):
        """Test that the AI can answer a simple question without using a tool."""
        # --- Setup Mocks ---
        # AI's response: Answer directly without calling a tool.
        mock_ollama_chat.return_value = {
            'message': {
                'role': 'assistant',
                'content': 'Hello! How can I help you today?',
                'tool_calls': None
            }
        }

        # --- Run Test ---
        messages = []
        response = query_swapbot("hello", messages)

        # --- Assertions ---
        # Verify that the response is the direct answer from the AI.
        self.assertEqual(response, 'Hello! How can I help you today?')

        # Verify that the conversation history contains just the user query and the AI's response.
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0]['role'], 'user')
        self.assertEqual(messages[1]['role'], 'assistant')

if __name__ == '__main__':
    unittest.main()
