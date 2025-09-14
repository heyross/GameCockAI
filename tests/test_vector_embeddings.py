"""
Comprehensive Test Suite for GameCock AI Vector Embeddings
Tests all components: vector database, embeddings, document processing, RAG system
"""

import unittest
import asyncio
import tempfile
import shutil
import numpy as np
import json
import os
import time
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Import the modules we're testing
import sys
import os
# Add path to find vector modules in src directory
src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../src'))
if src_dir not in sys.path:
    sys.path.append(src_dir)

try:
    from vector_db import VectorDBManager, GameCockVectorDB
    from embedding_service import FinancialEmbeddingService, EmbeddingOptimizer
    from document_processor import FinancialDocumentProcessor, DocumentType, DocumentChunk
    from rag_enhanced import EnhancedRAGSystem, QueryType, SearchResult
    from vector_integration import VectorIntegrationManager
    VECTOR_MODULES_AVAILABLE = True
except ImportError as e:
    VECTOR_MODULES_AVAILABLE = False
    print(f"⚠️  Vector modules not available for testing: {e}")

class TestVectorDatabase(unittest.TestCase):
    """Test vector database functionality"""
    
    def setUp(self):
        """Set up test environment"""
        if not VECTOR_MODULES_AVAILABLE:
            self.skipTest("Vector modules not available")
        
        self.test_dir = tempfile.mkdtemp()
        self.vector_db = GameCockVectorDB(persist_directory=self.test_dir)
        
    def tearDown(self):
        """Clean up test environment"""
        # Close vector database connection to release file locks
        if hasattr(self, 'vector_db'):
            try:
                self.vector_db.close()
            except Exception as e:
                print(f"Warning: Error closing vector database: {e}")
        
        # Clean up temporary directory
        if hasattr(self, 'test_dir') and os.path.exists(self.test_dir):
            try:
                shutil.rmtree(self.test_dir)
            except PermissionError as e:
                print(f"Warning: Could not remove test directory {self.test_dir}: {e}")
                # On Windows, try alternative cleanup
                import time
                time.sleep(0.1)  # Brief delay
                try:
                    shutil.rmtree(self.test_dir)
                except PermissionError:
                    print(f"Warning: Test directory {self.test_dir} may still be in use")
    
    def test_vector_db_initialization(self):
        """Test vector database initialization"""
        self.assertIsNotNone(self.vector_db.chroma_client)
        self.assertEqual(len(self.vector_db.collections), 0)
        self.assertEqual(len(self.vector_db.faiss_indexes), 0)
    
    def test_chroma_collection_creation(self):
        """Test ChromaDB collection creation"""
        # Use default sentence transformer embedding function for tests
        from chromadb.utils import embedding_functions
        default_ef = embedding_functions.DefaultEmbeddingFunction()
        
        success = self.vector_db.create_collection(
            name="test_collection",
            collection_type="chroma",
            embedding_function=default_ef,
            distance_metric="cosine"
        )
        
        self.assertTrue(success)
        self.assertIn("test_collection", self.vector_db.collections)
    
    def test_faiss_collection_creation(self):
        """Test FAISS collection creation"""
        success = self.vector_db.create_collection(
            name="test_faiss",
            collection_type="faiss",
            dimension=768,
            distance_metric="cosine"
        )
        
        self.assertTrue(success)
        self.assertIn("test_faiss", self.vector_db.faiss_indexes)
        self.assertEqual(self.vector_db.faiss_metadata["test_faiss"]["dimension"], 768)
    
    def test_document_addition_and_search(self):
        """Test adding documents and searching"""
        # Create collection with embedding function
        from chromadb.utils import embedding_functions
        default_ef = embedding_functions.DefaultEmbeddingFunction()
        
        self.vector_db.create_collection("test_docs", collection_type="chroma", embedding_function=default_ef)
        
        # Test documents
        documents = [
            "Apple Inc. is a technology company focused on consumer electronics.",
            "JPMorgan Chase is a major investment bank and financial services company.",
            "Tesla Inc. manufactures electric vehicles and energy storage systems."
        ]
        
        metadatas = [
            {"company": "Apple", "sector": "Technology"},
            {"company": "JPMorgan", "sector": "Financial Services"},
            {"company": "Tesla", "sector": "Automotive"}
        ]
        
        ids = ["doc_1", "doc_2", "doc_3"]
        
        # Add documents
        success = self.vector_db.add_documents(
            collection_name="test_docs",
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        self.assertTrue(success)
        
        # Test search
        results = self.vector_db.query_documents(
            collection_name="test_docs",
            query_texts=["technology company"],
            n_results=2
        )
        
        self.assertIn("documents", results)
        self.assertGreater(len(results["documents"][0]), 0)
    
    def test_vector_addition_and_search(self):
        """Test adding vectors to FAISS and searching"""
        # Create FAISS collection
        self.vector_db.create_collection(
            "test_vectors", 
            collection_type="faiss", 
            dimension=3
        )
        
        # Test vectors
        vectors = np.array([
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0], 
            [0.0, 0.0, 1.0]
        ])
        
        ids = ["vec_1", "vec_2", "vec_3"]
        metadatas = [{"type": "test"} for _ in ids]
        
        # Add vectors
        success = self.vector_db.add_vectors(
            collection_name="test_vectors",
            vectors=vectors,
            ids=ids,
            metadatas=metadatas
        )
        
        self.assertTrue(success)
        
        # Test search
        query_vector = np.array([[1.0, 0.1, 0.0]])
        distances, indices, external_ids = self.vector_db.query_vectors(
            collection_name="test_vectors",
            query_vectors=query_vector,
            k=2
        )
        
        self.assertEqual(len(distances[0]), 2)
        self.assertEqual(len(external_ids[0]), 2)


class TestEmbeddingService(unittest.TestCase):
    """Test embedding service functionality"""
    
    def setUp(self):
        """Set up test environment"""
        if not VECTOR_MODULES_AVAILABLE:
            self.skipTest("Vector modules not available")
        
        self.test_cache_dir = tempfile.mkdtemp()
        
        # Mock the sentence transformers to avoid downloading models in tests
        with patch('embedding_service.SentenceTransformer') as mock_st:
            mock_model = Mock()
            mock_model.encode.return_value = np.random.rand(3, 768)  # Mock embeddings
            mock_model.get_sentence_embedding_dimension.return_value = 768
            mock_model.device = "cpu"
            mock_st.return_value = mock_model
            
            self.embedding_service = FinancialEmbeddingService(
                cache_directory=self.test_cache_dir,
                enable_caching=True
            )
    
    def tearDown(self):
        """Clean up test environment"""
        if hasattr(self, 'test_cache_dir') and os.path.exists(self.test_cache_dir):
            shutil.rmtree(self.test_cache_dir)
    
    def test_embedding_generation(self):
        """Test basic embedding generation"""
        texts = [
            "Financial risk assessment for credit derivatives",
            "Market volatility in equity swap transactions"
        ]
        
        embeddings = self.embedding_service.embed_financial_documents(texts)
        
        self.assertEqual(embeddings.shape[0], 2)
        self.assertEqual(embeddings.shape[1], 768)
        self.assertIsInstance(embeddings, np.ndarray)
    
    def test_embedding_caching(self):
        """Test embedding caching functionality"""
        text = "Test financial document for caching"
        
        # First call - should generate embedding
        embeddings1 = self.embedding_service.embed_financial_documents([text])
        
        # Second call - should use cache
        embeddings2 = self.embedding_service.embed_financial_documents([text])
        
        np.testing.assert_array_equal(embeddings1, embeddings2)
    
    def test_market_data_embedding(self):
        """Test market data specific embedding"""
        market_summaries = [
            "Credit swap market showing increased volatility",
            "Equity derivatives trading volume up 15%"
        ]
        
        embeddings = self.embedding_service.embed_market_data(market_summaries, "swap")
        
        self.assertEqual(embeddings.shape[0], 2)
        self.assertGreater(embeddings.shape[1], 0)
    
    def test_company_profile_embedding(self):
        """Test company profile embedding"""
        company_texts = [
            "Apple Inc. is a multinational technology company",
            "JPMorgan Chase operates as an investment bank"
        ]
        
        embeddings = self.embedding_service.embed_company_profiles(company_texts)
        
        self.assertEqual(embeddings.shape[0], 2)
        self.assertGreater(embeddings.shape[1], 0)
    
    def test_batch_processing(self):
        """Test batch processing of large text sets"""
        large_text_set = [f"Financial document number {i}" for i in range(100)]
        
        embeddings = self.embedding_service.embed_financial_documents(large_text_set)
        
        self.assertEqual(embeddings.shape[0], 100)
        self.assertGreater(embeddings.shape[1], 0)


class TestDocumentProcessor(unittest.TestCase):
    """Test document processing functionality"""
    
    def setUp(self):
        """Set up test environment"""
        if not VECTOR_MODULES_AVAILABLE:
            self.skipTest("Vector modules not available")
        
        self.processor = FinancialDocumentProcessor(
            max_chunk_size=512,
            overlap_size=50,
            min_chunk_size=10  # Reduce minimum chunk size for tests
        )
    
    def test_sec_10k_processing(self):
        """Test SEC 10-K document processing"""
        test_10k = """
        ITEM 1A. RISK FACTORS
        
        Our business faces significant risks including market volatility,
        credit risks from counterparties, and regulatory changes affecting
        our operations. We maintain extensive risk management procedures
        to mitigate these risks.
        
        ITEM 2. PROPERTIES
        
        We own and lease facilities in major financial centers including
        New York, London, and Hong Kong. Our headquarters spans 2 million
        square feet of office space.
        """
        
        result = self.processor.process_document(
            test_10k,
            DocumentType.SEC_10K,
            {"company_name": "Test Corp", "cik": "1234567"}
        )
        
        self.assertIsNotNone(result)
        self.assertGreater(len(result.chunks), 0)
        self.assertIsNone(result.errors)
        
        # Check that sections were identified
        chunk_types = [chunk.chunk_type for chunk in result.chunks]
        self.assertTrue(any("risk" in ct.lower() for ct in chunk_types))
    
    def test_cftc_data_processing(self):
        """Test CFTC swap data processing"""
        test_cftc = """
        Trade ID: 12345, Asset Class: Credit, Notional: 10000000, Currency: USD
        Trade ID: 12346, Asset Class: Rates, Notional: 5000000, Currency: EUR
        Trade ID: 12347, Asset Class: Credit, Notional: 15000000, Currency: USD
        """
        
        result = self.processor.process_document(
            test_cftc,
            DocumentType.CFTC_SWAP,
            {"data_source": "CFTC", "date": "2024-01-01"}
        )
        
        self.assertIsNotNone(result)
        self.assertGreater(len(result.chunks), 0)
        self.assertEqual(result.chunks[0].chunk_type, "cftc_swap_data")
    
    def test_chunk_metadata_enhancement(self):
        """Test chunk metadata enhancement"""
        test_text = """
        Apple Inc. reported revenue of $94.9 billion and faces significant
        risks including supply chain disruptions and regulatory changes.
        The company maintains strong cash flow and debt management practices.
        """
        
        result = self.processor.process_document(
            test_text,
            DocumentType.SEC_10K,
            {"company_name": "Apple Inc", "cik": "0000320193"}
        )
        
        chunk = result.chunks[0]
        
        # Check enhanced metadata
        self.assertIn("financial_concepts", chunk.metadata)
        self.assertIn("contains_currency", chunk.metadata)
        self.assertIn("risk_indicators", chunk.metadata)
        self.assertGreater(chunk.metadata["risk_indicators"], 0)
    
    def test_importance_scoring(self):
        """Test chunk importance scoring"""
        high_importance_text = """
        RISK FACTORS: The company faces significant credit risk, market risk,
        and operational risk that could materially impact financial performance.
        Revenue declined 15% due to market volatility.
        """
        
        low_importance_text = """
        The company's headquarters address is 123 Main Street.
        Office hours are 9 AM to 5 PM Monday through Friday.
        """
        
        high_result = self.processor.process_document(
            high_importance_text, DocumentType.SEC_10K, {}
        )
        
        low_result = self.processor.process_document(
            low_importance_text, DocumentType.SEC_10K, {}
        )
        
        high_score = high_result.chunks[0].importance_score
        low_score = low_result.chunks[0].importance_score
        
        self.assertGreater(high_score, low_score)


class TestEnhancedRAGSystem(unittest.TestCase):
    """Test enhanced RAG system functionality"""
    
    def setUp(self):
        """Set up test environment"""
        if not VECTOR_MODULES_AVAILABLE:
            self.skipTest("Vector modules not available")
        
        self.test_dir = tempfile.mkdtemp()
        
        # Mock Ollama to avoid external dependencies
        self.ollama_patcher = patch('rag_enhanced.ollama.chat')
        self.mock_ollama = self.ollama_patcher.start()
        self.mock_ollama.return_value = {
            'message': {'content': 'Mock AI response based on provided context'}
        }
        
        # Mock embedding service
        with patch('rag_enhanced.FinancialEmbeddingService'):
            with patch('rag_enhanced.VectorDBManager'):
                with patch('rag_enhanced.FinancialDocumentProcessor'):
                    self.rag_system = EnhancedRAGSystem(
                        vector_store_path=self.test_dir,
                        cache_size=100
                    )
    
    def tearDown(self):
        """Clean up test environment"""
        self.ollama_patcher.stop()
        if hasattr(self, 'test_dir') and os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_query_classification(self):
        """Test query type classification"""
        test_cases = [
            ("What are Apple's risk factors?", QueryType.RISK_ASSESSMENT),  # Fixed: risk factors are risk assessment
            ("Show me recent market trends", QueryType.MARKET_TRENDS),
            ("Analyze credit risk exposure", QueryType.RISK_ASSESSMENT),
            ("SEC filing requirements", QueryType.REGULATORY_COMPLIANCE)
        ]
        
        for query, expected_type in test_cases:
            classified_type = self.rag_system._classify_query(query)
            self.assertEqual(classified_type, expected_type)
    
    def test_cache_functionality(self):
        """Test response caching"""
        query = "Test query for caching"
        
        # Mock search results
        mock_results = [
            SearchResult(
                chunk_id="test_1",
                content="Test content",
                metadata={"test": True},
                similarity_score=0.9,
                source_collection="test",
                rank=1
            )
        ]
        
        with patch.object(self.rag_system, '_semantic_search', return_value=mock_results):
            with patch.object(self.rag_system, '_build_enhanced_context', return_value="Test context"):
                with patch.object(self.rag_system, '_generate_response', return_value="Test response"):
                    
                    # First call
                    result1 = asyncio.run(self.rag_system.process_query(query))
                    
                    # Second call - should use cache
                    result2 = asyncio.run(self.rag_system.process_query(query))
                    
                    self.assertEqual(result1.answer, result2.answer)
                    self.assertTrue(result2.metadata.get("from_cache", False))
    
    def test_async_processing(self):
        """Test async query processing"""
        async def async_test():
            query = "Test async query"
            
            # Mock dependencies
            with patch.object(self.rag_system, '_semantic_search', return_value=[]):
                with patch.object(self.rag_system, '_build_enhanced_context', return_value=""):
                    with patch.object(self.rag_system, '_generate_response', return_value="Async response"):
                        
                        result = await self.rag_system.process_query(query)
                        
                        self.assertIsNotNone(result)
                        self.assertEqual(result.answer, "Async response")
                        self.assertGreaterEqual(result.processing_time, 0)  # Allow 0 for very fast operations
        
        # Run async test
        import asyncio
        asyncio.run(async_test())


class TestVectorIntegration(unittest.TestCase):
    """Test vector integration with existing systems"""
    
    def setUp(self):
        """Set up test environment"""
        if not VECTOR_MODULES_AVAILABLE:
            self.skipTest("Vector modules not available")
        
        self.test_dir = tempfile.mkdtemp()
        
        # Mock external dependencies
        with patch('vector_integration.VectorDBManager'):
            with patch('vector_integration.FinancialEmbeddingService'):
                with patch('vector_integration.EnhancedRAGSystem'):
                    with patch('vector_integration.SessionLocal'):
                        self.integration_manager = VectorIntegrationManager(
                            vector_store_path=self.test_dir,
                            initialize_collections=False,
                            preload_data=False
                        )
    
    def tearDown(self):
        """Clean up test environment"""
        if hasattr(self, 'test_dir') and os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_integration_status(self):
        """Test integration status reporting"""
        status = self.integration_manager.get_integration_status()
        
        self.assertIn("integration_status", status)
        self.assertIn("vector_database", status)
        self.assertIn("embedding_service", status)
        self.assertIn("last_updated", status)
    
    def test_vector_enhanced_analysis(self):
        """Test vector-enhanced company analysis"""
        async def async_test():
            # Mock the RAG system response
            mock_response = Mock()
            mock_response.answer = "Test analysis result"
            mock_response.confidence_score = 0.85
            mock_response.sources = []
            mock_response.processing_time = 0.5
            
            # Create async mock for process_query
            async def mock_process_query(*args, **kwargs):
                return mock_response
            
            with patch.object(self.integration_manager.rag_system, 'process_query', side_effect=mock_process_query):
                with patch.object(self.integration_manager.analytics_engine, 'execute_analytical_query', return_value={}):
                    
                    result = await self.integration_manager.vector_enhanced_company_analysis("0000320193")
                    
                    self.assertIn("semantic_analysis", result)
                    self.assertIn("traditional_analysis", result)
                    self.assertEqual(result["company_cik"], "0000320193")
        
        # Run async test  
        import asyncio
        asyncio.run(async_test())


class TestPerformance(unittest.TestCase):
    """Performance and benchmark tests"""
    
    def setUp(self):
        """Set up performance test environment"""
        if not VECTOR_MODULES_AVAILABLE:
            self.skipTest("Vector modules not available")
    
    def test_embedding_performance(self):
        """Test embedding generation performance"""
        # Mock embedding service for performance testing
        with patch('embedding_service.SentenceTransformer') as mock_st:
            mock_model = Mock()
            mock_model.encode.return_value = np.random.rand(100, 768)
            mock_model.get_sentence_embedding_dimension.return_value = 768
            mock_st.return_value = mock_model
            
            service = FinancialEmbeddingService()
            
            # Test batch processing performance
            large_text_set = [f"Financial document {i}" for i in range(100)]
            
            start_time = time.time()
            embeddings = service.embed_financial_documents(large_text_set)
            elapsed_time = time.time() - start_time
            
            # Should process 100 documents reasonably quickly
            self.assertLess(elapsed_time, 10.0)  # Less than 10 seconds
            self.assertEqual(embeddings.shape[0], 100)
    
    def test_vector_search_performance(self):
        """Test vector search performance"""
        test_dir = tempfile.mkdtemp()
        
        try:
            vector_db = GameCockVectorDB(persist_directory=test_dir)
            
            # Use default embedding function for performance test
            from chromadb.utils import embedding_functions
            default_ef = embedding_functions.DefaultEmbeddingFunction()
            
            vector_db.create_collection("perf_test", collection_type="chroma", embedding_function=default_ef)
            
            # Add many documents for performance testing
            documents = [f"Test document {i} with financial content" for i in range(1000)]
            metadatas = [{"doc_id": i} for i in range(1000)]
            ids = [f"doc_{i}" for i in range(1000)]
            
            # Mock embeddings
            with patch.object(vector_db.collections["perf_test"], 'add') as mock_add:
                mock_add.return_value = True
                
                start_time = time.time()
                success = vector_db.add_documents(
                    collection_name="perf_test",
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )
                elapsed_time = time.time() - start_time
                
                self.assertTrue(success)
                self.assertLess(elapsed_time, 5.0)  # Should be fast with mocked data
        
        finally:
            try:
                shutil.rmtree(test_dir)
            except PermissionError as e:
                print(f"Warning: Could not remove test directory {test_dir}: {e}")
                # On Windows, try alternative cleanup
                import time as time_module
                time_module.sleep(0.1)  # Brief delay
                try:
                    shutil.rmtree(test_dir)
                except PermissionError:
                    print(f"Warning: Test directory {test_dir} may still be in use")


class TestErrorHandling(unittest.TestCase):
    """Test error handling and edge cases"""
    
    def setUp(self):
        """Set up error testing environment"""
        if not VECTOR_MODULES_AVAILABLE:
            self.skipTest("Vector modules not available")
    
    def test_invalid_collection_operations(self):
        """Test operations on invalid collections"""
        test_dir = tempfile.mkdtemp()
        
        try:
            vector_db = GameCockVectorDB(persist_directory=test_dir)
            
            # Try to add to non-existent collection
            success = vector_db.add_documents(
                collection_name="nonexistent",
                documents=["test"],
                metadatas=[{}],
                ids=["test"]
            )
            
            self.assertFalse(success)
            
            # Try to query non-existent collection
            results = vector_db.query_documents(
                collection_name="nonexistent",
                query_texts=["test"]
            )
            
            self.assertIn("error", results)
        
        finally:
            try:
                shutil.rmtree(test_dir)
            except PermissionError as e:
                print(f"Warning: Could not remove test directory {test_dir}: {e}")
                # On Windows, try alternative cleanup
                import time as time_module
                time_module.sleep(0.1)  # Brief delay
                try:
                    shutil.rmtree(test_dir)
                except PermissionError:
                    print(f"Warning: Test directory {test_dir} may still be in use")
    
    def test_empty_document_processing(self):
        """Test processing empty or malformed documents"""
        processor = FinancialDocumentProcessor()
        
        # Test empty document
        result = processor.process_document("", DocumentType.SEC_10K, {})
        self.assertEqual(len(result.chunks), 0)
        
        # Test very short document
        result = processor.process_document("Short", DocumentType.SEC_10K, {})
        # Should handle gracefully
        self.assertIsNotNone(result)
    
    def test_embedding_service_failures(self):
        """Test embedding service error handling"""
        # Mock a failing model
        with patch('embedding_service.SentenceTransformer') as mock_st:
            mock_st.side_effect = Exception("Model loading failed")
            
            with self.assertRaises(Exception):
                FinancialEmbeddingService()


class TestEndToEndIntegration(unittest.TestCase):
    """End-to-end integration tests"""
    
    def setUp(self):
        """Set up end-to-end test environment"""
        if not VECTOR_MODULES_AVAILABLE:
            self.skipTest("Vector modules not available")
        
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test environment"""
        if hasattr(self, 'test_dir') and os.path.exists(self.test_dir):
            try:
                shutil.rmtree(self.test_dir)
            except PermissionError as e:
                print(f"Warning: Could not remove test directory {self.test_dir}: {e}")
                # On Windows, try alternative cleanup
                import time
                time.sleep(0.1)  # Brief delay
                try:
                    shutil.rmtree(self.test_dir)
                except PermissionError:
                    print(f"Warning: Test directory {self.test_dir} may still be in use")
    
    def test_full_pipeline_mock(self):
        """Test the full pipeline with mocked components"""
        # Mock all external dependencies
        with patch('vector_integration.VectorDBManager') as mock_vdb:
            with patch('vector_integration.FinancialEmbeddingService') as mock_emb:
                with patch('vector_integration.EnhancedRAGSystem') as mock_rag:
                    with patch('vector_integration.SessionLocal'):
                        
                        # Set up mocks
                        mock_vdb_instance = Mock()
                        mock_vdb.return_value = mock_vdb_instance
                        
                        mock_emb_instance = Mock()
                        mock_emb.return_value = mock_emb_instance
                        
                        mock_rag_instance = Mock()
                        mock_rag.return_value = mock_rag_instance
                        
                        # Mock responses
                        mock_response = Mock()
                        mock_response.answer = "Comprehensive analysis result"
                        mock_response.confidence_score = 0.9
                        mock_response.sources = []
                        mock_response.processing_time = 0.3
                        
                        async def mock_process_query(*args, **kwargs):
                            return mock_response
                        
                        mock_rag_instance.process_query = mock_process_query
                        
                        # Test the integration
                        manager = VectorIntegrationManager(
                            vector_store_path=self.test_dir,
                            initialize_collections=False
                        )
                        
                        # Test company analysis
                        result = asyncio.run(
                            manager.vector_enhanced_company_analysis("0000320193")
                        )
                        
                        self.assertIn("semantic_analysis", result)
                        self.assertEqual(result["company_cik"], "0000320193")


def run_all_tests():
    """Run all test suites and generate report"""
    print("🧪 Running GameCock AI Vector Embeddings Test Suite")
    print("=" * 60)
    
    # Test suites to run
    test_classes = [
        TestVectorDatabase,
        TestEmbeddingService, 
        TestDocumentProcessor,
        TestEnhancedRAGSystem,
        TestVectorIntegration,
        TestPerformance,
        TestErrorHandling,
        TestEndToEndIntegration
    ]
    
    total_tests = 0
    total_failures = 0
    total_errors = 0
    
    for test_class in test_classes:
        print(f"\n📋 Running {test_class.__name__}...")
        
        suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        total_tests += result.testsRun
        total_failures += len(result.failures)
        total_errors += len(result.errors)
        
        if result.failures:
            print(f"❌ Failures in {test_class.__name__}:")
            for test, failure in result.failures:
                print(f"   - {test}: {failure}")
        
        if result.errors:
            print(f"💥 Errors in {test_class.__name__}:")
            for test, error in result.errors:
                print(f"   - {test}: {error}")
    
    # Final report
    print("\n" + "=" * 60)
    print("🏁 TEST SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {total_tests}")
    print(f"Failures: {total_failures}")
    print(f"Errors: {total_errors}")
    
    if total_failures == 0 and total_errors == 0:
        print("✅ ALL TESTS PASSED!")
        return True
    else:
        print("❌ Some tests failed - see details above")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
