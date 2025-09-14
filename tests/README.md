# 🧪 GameCock AI Vector Embeddings Test Suite

Comprehensive testing infrastructure for the GameCock AI vector embeddings system.

## 📋 Test Overview

This test suite validates all aspects of the vector embeddings implementation:

### Test Types

1. **Unit Tests** (`test_vector_embeddings.py`)
   - Tests individual components with mocked dependencies
   - Fast execution, no external dependencies
   - Covers edge cases and error conditions

2. **Performance Benchmarks** (`test_performance_benchmarks.py`)
   - Measures actual performance with realistic data loads
   - Tests scalability and resource usage
   - Generates performance reports

3. **Real Integration Tests** (`test_real_integration.py`)
   - End-to-end testing with actual vector operations
   - Tests real embedding models (if available)
   - Validates complete workflows

4. **Test Data Generators** (`test_data_generators.py`)
   - Generates realistic financial test data
   - Creates mock databases and documents
   - Provides utilities for test setup

## 🚀 Quick Start

### Run All Tests
```bash
# Run complete test suite from GameCockAI/tests/ directory
cd GameCockAI/tests
python run_all_tests.py

# Run with verbose output
python run_all_tests.py --verbose

# Skip slow tests
python run_all_tests.py --skip-performance --skip-integration
```

### Run Individual Test Suites
```bash
# Unit tests only
python test_vector_embeddings.py

# Performance benchmarks only  
python test_performance_benchmarks.py

# Integration tests only
python test_real_integration.py
```

### Generate Test Data
```bash
# Generate test data for manual testing
python test_data_generators.py
```

## 📊 Test Results

Test results are saved to `./test_results/` directory:

- `test_results_YYYYMMDD_HHMMSS.json` - Detailed JSON results
- `test_report_YYYYMMDD_HHMMSS.txt` - Human-readable report

### Sample Output
```
🧪 GameCock AI Vector Embeddings Test Report
============================================================
Generated: 2024-01-15 14:30:25
Duration: 45.2 seconds

🔍 ENVIRONMENT
Python: 3.9.7
Platform: Windows-10-10.0.19045-SP0
Vector modules: Available
CUDA support: Available

📊 SUMMARY
Test suites run: 3
Passed: 3
Failed: 0
Pass rate: 100.0%
Overall success: ✅ Yes

📋 TEST SUITE RESULTS
Unit Tests: ✅ PASS (CRITICAL) - 12.5s
Performance Benchmarks: ✅ PASS - 18.7s
Real Integration Tests: ✅ PASS (CRITICAL) - 14.0s

💡 RECOMMENDATIONS
✅ All critical tests passed - system ready for deployment
⚡ Consider GPU acceleration for better performance
```

## 🧩 Test Components

### Vector Database Tests
- ChromaDB collection creation and operations
- FAISS index creation and vector search
- Persistence and data recovery
- Concurrent access patterns

### Embedding Service Tests
- Model loading and initialization
- Financial text embedding generation
- Batch processing performance
- Caching effectiveness
- Domain-specific embeddings

### Document Processing Tests
- SEC filing chunking and processing
- CFTC data processing
- Metadata enhancement
- Importance scoring
- Error handling

### RAG System Tests
- Query classification
- Semantic search
- Context building
- Response generation
- Caching and performance

### Integration Tests
- End-to-end document pipeline
- Cross-dataset correlation
- Real-world query processing
- System health checks

## ⚡ Performance Benchmarks

### Embedding Generation
- Batch size optimization
- Throughput measurement
- Memory usage patterns
- Caching effectiveness

### Vector Search
- Search latency by database size
- Concurrent query handling
- Index optimization
- Scalability limits

### End-to-End Performance
- Query processing time
- Memory consumption
- Concurrent user simulation
- Resource utilization

## 🛠️ Test Configuration

### Environment Variables
```bash
# Optional: specify test data directory
export TEST_DATA_DIR="./custom_test_data"

# Optional: specify vector store path
export VECTOR_STORE_PATH="./test_vector_store"

# Optional: enable GPU testing
export ENABLE_GPU_TESTS="true"
```

### Test Configuration File
Create `test_config.json`:
```json
{
  "test_settings": {
    "run_performance_tests": true,
    "run_integration_tests": true,
    "max_test_documents": 1000,
    "performance_timeout": 300
  },
  "vector_settings": {
    "embedding_dimension": 768,
    "batch_size": 32,
    "enable_caching": true
  }
}
```

## 🐛 Troubleshooting

### Common Issues

#### "Vector modules not available"
**Solution**: Install the vector embeddings system:
```bash
cd ../../  # Go back to root directory
python vector_setup.py
```

#### "Embedding models not found"
**Solution**: Models will be downloaded automatically on first use, or manually:
```bash
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('ProsusAI/finbert')"
```

#### Tests timeout or run slowly
**Solution**: 
- Use `--skip-performance` for faster testing
- Reduce test data size in configuration
- Ensure adequate system resources

#### "CUDA not available" warnings
**Solution**: Install PyTorch with CUDA support:
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

#### Permission errors on Windows
**Solution**: Run as administrator or check file permissions

### Debug Mode
```bash
# Run with debug output
python run_all_tests.py --verbose

# Run individual test with more detail
python -m unittest test_vector_embeddings.TestVectorDatabase.test_vector_db_initialization -v
```

## 📈 Performance Targets

### Speed Targets
- Embedding generation: > 100 docs/second
- Vector search: < 100ms for 10k documents
- End-to-end query: < 500ms

### Quality Targets
- Unit test coverage: > 90%
- Integration test pass rate: 100%
- Performance regression: < 10%

### Resource Targets
- Memory usage: < 2GB for test suite
- CPU utilization: < 80% average
- Storage: < 1GB for test data

## 🔄 Continuous Integration

### GitHub Actions Example
```yaml
name: Vector Embeddings Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        python vector_setup.py
    - name: Run tests
      run: cd GameCockAI/tests && python run_all_tests.py
```

### Pre-commit Hook
```bash
#!/bin/bash
# .git/hooks/pre-commit
echo "Running vector embeddings tests..."
cd GameCockAI/tests
python run_all_tests.py --skip-performance
if [ $? -ne 0 ]; then
    echo "Tests failed - commit aborted"
    exit 1
fi
```

## 📝 Writing New Tests

### Adding Unit Tests
```python
class TestNewFeature(unittest.TestCase):
    def setUp(self):
        self.feature = NewFeature()
    
    def test_basic_functionality(self):
        result = self.feature.process("test input")
        self.assertIsNotNone(result)
        self.assertEqual(result.status, "success")
```

### Adding Performance Tests
```python
def test_new_feature_performance(self):
    start_time = time.time()
    result = self.feature.bulk_process(large_dataset)
    elapsed = time.time() - start_time
    
    self.assertLess(elapsed, 10.0)  # Must complete in 10s
    self.assertEqual(len(result), len(large_dataset))
```

### Adding Integration Tests
```python
def test_new_feature_integration(self):
    # Set up real components
    vector_db = GameCockVectorDB("./test_vector_store")
    
    # Test real operations
    result = self.feature.integrate_with_vector_db(vector_db)
    
    # Verify integration
    self.assertTrue(result.success)
    self.assertGreater(len(result.data), 0)
```

## 🎯 Test Maintenance

### Regular Tasks
- Update test data monthly
- Review performance benchmarks
- Check for deprecated APIs
- Update documentation

### Release Testing
- Full test suite with all options
- Performance regression testing
- Load testing with production data sizes
- Security and error handling validation

## 📍 Location and Import Notes

This test suite is located in `GameCockAI/tests/` and imports vector modules from the root directory using:
```python
sys.path.append('../..')
```

All tests are designed to work from the GameCockAI/tests directory. If you need to run tests from elsewhere, adjust the import paths accordingly.

This comprehensive test suite ensures the GameCock AI vector embeddings system is robust, performant, and ready for production deployment! 🚀
