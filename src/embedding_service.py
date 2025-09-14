"""
Financial Embedding Service for GameCock AI
Provides specialized embedding generation for financial documents and data
"""

import numpy as np
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModel

# Lazy import torch to avoid Windows loading issues
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    torch = None
import hashlib
import pickle
import os
from typing import List, Dict, Any, Optional, Union, Tuple
import logging
import time
from functools import lru_cache
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import tiktoken

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FinancialEmbeddingService:
    """
    Specialized embedding service for financial documents and data
    Supports multiple embedding models optimized for different financial content types
    """
    
    def __init__(self, 
                 cache_directory: str = "./embedding_cache",
                 device: str = "auto",
                 batch_size: int = 32,
                 enable_caching: bool = True):
        """
        Initialize the Financial Embedding Service
        
        Args:
            cache_directory: Directory for embedding cache
            device: Device for model inference ("auto", "cpu", "cuda")
            batch_size: Batch size for embedding generation
            enable_caching: Whether to enable embedding caching
        """
        self.cache_directory = cache_directory
        self.batch_size = batch_size
        self.enable_caching = enable_caching
        
        # Set device
        if device == "auto":
            self.device = "cuda" if TORCH_AVAILABLE and torch.cuda.is_available() else "cpu"
        else:
            self.device = device
        
        logger.info(f"Using device: {self.device}")
        
        # Initialize cache
        if enable_caching:
            self._init_cache()
        
        # Initialize models
        self.models = {}
        self.tokenizers = {}
        self._load_models()
        
        # Thread lock for cache operations
        self._cache_lock = threading.Lock()
        
        logger.info("FinancialEmbeddingService initialized successfully")
    
    def _init_cache(self):
        """Initialize embedding cache directory and structures"""
        if not os.path.exists(self.cache_directory):
            os.makedirs(self.cache_directory)
        
        self.cache_files = {
            "finbert": os.path.join(self.cache_directory, "finbert_cache.pkl"),
            "e5": os.path.join(self.cache_directory, "e5_cache.pkl"),
            "general": os.path.join(self.cache_directory, "general_cache.pkl")
        }
        
        # Load existing caches
        self.embedding_caches = {}
        for model_name, cache_file in self.cache_files.items():
            if os.path.exists(cache_file):
                try:
                    with open(cache_file, 'rb') as f:
                        self.embedding_caches[model_name] = pickle.load(f)
                    logger.info(f"Loaded {len(self.embedding_caches[model_name])} cached embeddings for {model_name}")
                except Exception as e:
                    logger.warning(f"Failed to load cache for {model_name}: {e}")
                    self.embedding_caches[model_name] = {}
            else:
                self.embedding_caches[model_name] = {}
    
    def _load_models(self):
        """Load pre-trained embedding models"""
        try:
            # FinBERT for financial text understanding
            logger.info("Loading FinBERT model...")
            self.models["finbert"] = SentenceTransformer('ProsusAI/finbert')
            self.models["finbert"].to(self.device)
            
            # E5-Large-v2 for general semantic understanding
            logger.info("Loading E5-Large-v2 model...")
            self.models["e5"] = SentenceTransformer('intfloat/e5-large-v2')
            self.models["e5"].to(self.device)
            
            # Initialize tokenizers
            self.tokenizers["finbert"] = AutoTokenizer.from_pretrained('ProsusAI/finbert')
            self.tokenizers["e5"] = AutoTokenizer.from_pretrained('intfloat/e5-large-v2')
            
            # Initialize tiktoken for OpenAI-style tokenization
            self.tiktoken_encoder = tiktoken.get_encoding("cl100k_base")
            
            logger.info("All embedding models loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load embedding models: {e}")
            raise
    
    def embed_financial_documents(self, 
                                 texts: List[str], 
                                 use_cache: bool = True,
                                 model: str = "finbert") -> np.ndarray:
        """
        Generate embeddings for financial documents
        
        Args:
            texts: List of document texts
            use_cache: Whether to use cached embeddings
            model: Model to use ("finbert", "e5")
            
        Returns:
            numpy array of embeddings
        """
        if not texts:
            return np.array([])
        
        try:
            # Check cache first
            if use_cache and self.enable_caching:
                cached_embeddings, uncached_texts, uncached_indices = self._check_cache(texts, model)
            else:
                cached_embeddings = []
                uncached_texts = texts
                uncached_indices = list(range(len(texts)))
            
            # Generate embeddings for uncached texts
            new_embeddings = []
            if uncached_texts:
                logger.info(f"Generating embeddings for {len(uncached_texts)} texts using {model}")
                start_time = time.time()
                
                # Preprocess texts for financial content
                preprocessed_texts = self._preprocess_financial_texts(uncached_texts)
                
                # Generate embeddings in batches
                new_embeddings = self._batch_embed(preprocessed_texts, model)
                
                elapsed_time = time.time() - start_time
                logger.info(f"Generated {len(new_embeddings)} embeddings in {elapsed_time:.2f} seconds")
                
                # Cache new embeddings
                if use_cache and self.enable_caching:
                    self._cache_embeddings(uncached_texts, new_embeddings, model)
            
            # Combine cached and new embeddings
            all_embeddings = self._combine_embeddings(
                texts, cached_embeddings, new_embeddings, uncached_indices
            )
            
            return all_embeddings
            
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            raise
    
    def embed_financial_concepts(self, 
                                concepts: List[str],
                                context: str = "",
                                model: str = "finbert") -> np.ndarray:
        """
        Generate embeddings for financial concepts with optional context
        
        Args:
            concepts: List of financial concepts/terms
            context: Optional context to enhance concept understanding
            model: Model to use for embedding generation
            
        Returns:
            numpy array of concept embeddings
        """
        try:
            # Enhance concepts with context if provided
            if context:
                enhanced_concepts = [
                    f"In the context of {context}: {concept}" 
                    for concept in concepts
                ]
            else:
                enhanced_concepts = concepts
            
            # Add financial domain prefixes for better understanding
            financial_enhanced = [
                f"Financial concept: {concept}" 
                for concept in enhanced_concepts
            ]
            
            return self.embed_financial_documents(financial_enhanced, model=model)
            
        except Exception as e:
            logger.error(f"Failed to generate concept embeddings: {e}")
            raise
    
    def embed_market_data(self, 
                         market_summaries: List[str],
                         data_type: str = "general") -> np.ndarray:
        """
        Generate embeddings for market data summaries
        
        Args:
            market_summaries: List of market data summary texts
            data_type: Type of market data ("swap", "equity", "commodity", "general")
            
        Returns:
            numpy array of embeddings
        """
        try:
            # Add domain-specific prefixes based on data type
            prefix_map = {
                "swap": "Swap market data: ",
                "equity": "Equity market data: ",
                "commodity": "Commodity market data: ",
                "forex": "Foreign exchange data: ",
                "general": "Market data: "
            }
            
            prefix = prefix_map.get(data_type, "Market data: ")
            enhanced_summaries = [f"{prefix}{summary}" for summary in market_summaries]
            
            # Use E5 model for market data (better for structured data)
            return self.embed_financial_documents(enhanced_summaries, model="e5")
            
        except Exception as e:
            logger.error(f"Failed to generate market data embeddings: {e}")
            raise
    
    def embed_company_profiles(self, 
                              company_texts: List[str],
                              include_metadata: bool = True) -> np.ndarray:
        """
        Generate embeddings for company profile texts
        
        Args:
            company_texts: List of company description/profile texts
            include_metadata: Whether to include company metadata in embedding
            
        Returns:
            numpy array of company profile embeddings
        """
        try:
            if include_metadata:
                # Enhance with company-specific context
                enhanced_texts = [
                    f"Company profile and business description: {text}"
                    for text in company_texts
                ]
            else:
                enhanced_texts = company_texts
            
            # Use FinBERT for company profiles (better financial understanding)
            return self.embed_financial_documents(enhanced_texts, model="finbert")
            
        except Exception as e:
            logger.error(f"Failed to generate company profile embeddings: {e}")
            raise
    
    def _preprocess_financial_texts(self, texts: List[str]) -> List[str]:
        """
        Preprocess financial texts for better embedding quality
        
        Args:
            texts: Raw input texts
            
        Returns:
            Preprocessed texts
        """
        preprocessed = []
        
        for text in texts:
            # Clean and normalize text
            cleaned_text = self._clean_financial_text(text)
            
            # Truncate to model limits if necessary
            truncated_text = self._truncate_text(cleaned_text, max_tokens=512)
            
            preprocessed.append(truncated_text)
        
        return preprocessed
    
    def _clean_financial_text(self, text: str) -> str:
        """Clean and normalize financial text"""
        import re
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Normalize financial terms
        text = re.sub(r'\$\s*(\d)', r'$\1', text)  # Fix dollar sign spacing
        text = re.sub(r'(\d)\s*%', r'\1%', text)   # Fix percentage spacing
        
        # Remove HTML entities if present
        text = re.sub(r'&[a-zA-Z]+;', ' ', text)
        
        # Remove excess punctuation
        text = re.sub(r'[.,!?;]{2,}', '.', text)
        
        return text.strip()
    
    def _truncate_text(self, text: str, max_tokens: int = 512) -> str:
        """Truncate text to maximum token length"""
        try:
            tokens = self.tiktoken_encoder.encode(text)
            if len(tokens) <= max_tokens:
                return text
            
            # Truncate tokens and decode back to text
            truncated_tokens = tokens[:max_tokens]
            return self.tiktoken_encoder.decode(truncated_tokens)
            
        except Exception:
            # Fallback to character-based truncation
            char_limit = max_tokens * 4  # Rough estimate
            return text[:char_limit] if len(text) > char_limit else text
    
    def _batch_embed(self, texts: List[str], model: str) -> np.ndarray:
        """Generate embeddings in batches for efficiency"""
        if model not in self.models:
            raise ValueError(f"Model {model} not available")
        
        embeddings = []
        model_instance = self.models[model]
        
        # Process in batches
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            
            try:
                # Generate embeddings for batch
                batch_embeddings = model_instance.encode(
                    batch,
                    device=self.device,
                    show_progress_bar=False,
                    convert_to_numpy=True,
                    normalize_embeddings=True  # Normalize for cosine similarity
                )
                embeddings.append(batch_embeddings)
                
            except Exception as e:
                logger.error(f"Failed to process batch {i//self.batch_size}: {e}")
                # Add zero embeddings for failed batch
                embedding_dim = model_instance.get_sentence_embedding_dimension()
                zero_embeddings = np.zeros((len(batch), embedding_dim))
                embeddings.append(zero_embeddings)
        
        return np.vstack(embeddings) if embeddings else np.array([])
    
    def _check_cache(self, texts: List[str], model: str) -> Tuple[List, List[str], List[int]]:
        """Check cache for existing embeddings"""
        if model not in self.embedding_caches:
            return [], texts, list(range(len(texts)))
        
        cache = self.embedding_caches[model]
        cached_embeddings = []
        uncached_texts = []
        uncached_indices = []
        
        for i, text in enumerate(texts):
            cache_key = self._get_cache_key(text)
            
            if cache_key in cache:
                cached_embeddings.append((i, cache[cache_key]))
            else:
                uncached_texts.append(text)
                uncached_indices.append(i)
        
        return cached_embeddings, uncached_texts, uncached_indices
    
    def _cache_embeddings(self, texts: List[str], embeddings: np.ndarray, model: str):
        """Cache generated embeddings"""
        if model not in self.embedding_caches:
            return
        
        with self._cache_lock:
            cache = self.embedding_caches[model]
            
            for text, embedding in zip(texts, embeddings):
                cache_key = self._get_cache_key(text)
                cache[cache_key] = embedding
            
            # Save cache to disk periodically
            if len(cache) % 100 == 0:  # Save every 100 new embeddings
                self._save_cache(model)
    
    def _save_cache(self, model: str):
        """Save embedding cache to disk"""
        try:
            # Check if we have the necessary attributes and builtins available
            if not hasattr(self, 'cache_files') or model not in self.cache_files:
                return
            
            cache_file = self.cache_files[model]
            with open(cache_file, 'wb') as f:
                pickle.dump(self.embedding_caches[model], f)
            logger.debug(f"Saved {len(self.embedding_caches[model])} cached embeddings for {model}")
        except (NameError, AttributeError) as e:
            # Handle cases where builtins or attributes are not available (e.g., during garbage collection)
            logger.debug(f"Cache save skipped for {model} due to unavailable resources: {e}")
        except Exception as e:
            logger.error(f"Failed to save cache for {model}: {e}")
    
    def _get_cache_key(self, text: str) -> str:
        """Generate cache key for text"""
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    def _combine_embeddings(self, 
                           texts: List[str],
                           cached_embeddings: List[Tuple[int, np.ndarray]],
                           new_embeddings: np.ndarray,
                           uncached_indices: List[int]) -> np.ndarray:
        """Combine cached and new embeddings in correct order"""
        if not texts:
            return np.array([])
        
        # Get embedding dimension
        if cached_embeddings:
            embedding_dim = cached_embeddings[0][1].shape[0]
        elif len(new_embeddings) > 0:
            embedding_dim = new_embeddings.shape[1]
        else:
            # Default dimension for FinBERT
            embedding_dim = 768
        
        # Initialize result array
        result = np.zeros((len(texts), embedding_dim))
        
        # Place cached embeddings
        for idx, embedding in cached_embeddings:
            result[idx] = embedding
        
        # Place new embeddings
        for i, idx in enumerate(uncached_indices):
            if i < len(new_embeddings):
                result[idx] = new_embeddings[i]
        
        return result
    
    def get_model_info(self, model: str) -> Dict[str, Any]:
        """Get information about a specific model"""
        if model not in self.models:
            return {"error": f"Model {model} not loaded"}
        
        model_instance = self.models[model]
        
        return {
            "model_name": model,
            "embedding_dimension": model_instance.get_sentence_embedding_dimension(),
            "max_sequence_length": getattr(model_instance, 'max_seq_length', 512),
            "device": str(model_instance.device),
            "cached_embeddings": len(self.embedding_caches.get(model, {}))
        }
    
    def get_embedding_stats(self) -> Dict[str, Any]:
        """Get comprehensive embedding service statistics"""
        stats = {
            "models_loaded": list(self.models.keys()),
            "device": self.device,
            "batch_size": self.batch_size,
            "caching_enabled": self.enable_caching,
            "cache_statistics": {}
        }
        
        if self.enable_caching:
            for model_name, cache in self.embedding_caches.items():
                stats["cache_statistics"][model_name] = {
                    "cached_embeddings": len(cache),
                    "cache_file": self.cache_files.get(model_name, "N/A")
                }
        
        return stats
    
    def clear_cache(self, model: Optional[str] = None):
        """Clear embedding cache for specified model or all models"""
        if model:
            if model in self.embedding_caches:
                self.embedding_caches[model] = {}
                logger.info(f"Cleared cache for {model}")
        else:
            for model_name in self.embedding_caches:
                self.embedding_caches[model_name] = {}
            logger.info("Cleared all embedding caches")
    
    def save_all_caches(self):
        """Save all embedding caches to disk"""
        for model in self.embedding_caches:
            self._save_cache(model)
        logger.info("All embedding caches saved to disk")
    
    def precompute_embeddings(self, 
                             texts: List[str], 
                             model: str = "finbert",
                             save_progress: bool = True) -> np.ndarray:
        """
        Precompute embeddings for a large set of texts
        Useful for bulk preprocessing of document collections
        
        Args:
            texts: List of texts to embed
            model: Model to use for embedding
            save_progress: Whether to save cache periodically during processing
            
        Returns:
            Array of computed embeddings
        """
        logger.info(f"Precomputing embeddings for {len(texts)} texts using {model}")
        
        try:
            # Split into manageable chunks
            chunk_size = 1000
            all_embeddings = []
            
            for i in range(0, len(texts), chunk_size):
                chunk = texts[i:i + chunk_size]
                chunk_embeddings = self.embed_financial_documents(chunk, model=model)
                all_embeddings.append(chunk_embeddings)
                
                logger.info(f"Processed chunk {i//chunk_size + 1}/{(len(texts) + chunk_size - 1)//chunk_size}")
                
                # Save progress periodically
                if save_progress and (i + chunk_size) % (chunk_size * 5) == 0:
                    self._save_cache(model)
            
            # Final save
            if save_progress:
                self._save_cache(model)
            
            result = np.vstack(all_embeddings) if all_embeddings else np.array([])
            logger.info(f"Precomputation complete: {result.shape}")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to precompute embeddings: {e}")
            raise
    
    def __del__(self):
        """Cleanup when service is destroyed"""
        try:
            # Check if we still have access to builtins (avoid errors during garbage collection)
            if hasattr(self, 'enable_caching') and self.enable_caching and 'open' in dir(__builtins__):
                self.save_all_caches()
        except Exception:
            pass  # Ignore errors during cleanup


class EmbeddingOptimizer:
    """
    Utility class for optimizing embedding operations
    """
    
    @staticmethod
    def optimize_batch_size(texts: List[str], 
                           embedding_service: FinancialEmbeddingService,
                           target_memory_gb: float = 2.0) -> int:
        """
        Determine optimal batch size based on available memory and text lengths
        
        Args:
            texts: Sample texts for estimation
            embedding_service: Embedding service instance
            target_memory_gb: Target memory usage in GB
            
        Returns:
            Recommended batch size
        """
        if not texts:
            return 32
        
        # Estimate memory usage per text
        avg_length = np.mean([len(text) for text in texts[:100]])
        estimated_memory_per_text = avg_length * 0.001  # Rough estimate in MB
        
        # Calculate batch size
        target_memory_mb = target_memory_gb * 1024
        estimated_batch_size = int(target_memory_mb / estimated_memory_per_text)
        
        # Clamp to reasonable range
        batch_size = max(8, min(256, estimated_batch_size))
        
        logger.info(f"Recommended batch size: {batch_size} (avg text length: {avg_length:.0f} chars)")
        return batch_size
    
    @staticmethod
    def benchmark_models(texts: List[str], 
                        embedding_service: FinancialEmbeddingService) -> Dict[str, Dict[str, float]]:
        """
        Benchmark different embedding models on sample texts
        
        Args:
            texts: Sample texts for benchmarking
            embedding_service: Embedding service instance
            
        Returns:
            Performance metrics for each model
        """
        models = ["finbert", "e5"]
        results = {}
        
        for model in models:
            start_time = time.time()
            try:
                embeddings = embedding_service.embed_financial_documents(texts[:10], model=model)
                elapsed = time.time() - start_time
                
                results[model] = {
                    "time_per_text": elapsed / len(texts[:10]),
                    "embeddings_per_second": len(texts[:10]) / elapsed,
                    "embedding_dimension": embeddings.shape[1] if len(embeddings) > 0 else 0,
                    "success": True
                }
            except Exception as e:
                results[model] = {
                    "error": str(e),
                    "success": False
                }
        
        return results

