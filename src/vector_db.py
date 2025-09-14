"""
Vector Database Management for GameCock AI
Provides ChromaDB and FAISS integration for high-performance semantic search
"""

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
import faiss
import numpy as np
import pickle
import os
from typing import List, Dict, Any, Optional, Tuple
import sqlite3
import json
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GameCockVectorDB:
    """
    Hybrid vector database system combining ChromaDB for document-level search
    and FAISS for high-performance numerical data search
    """
    
    def __init__(self, persist_directory: str = "./vector_store"):
        """
        Initialize the vector database system
        
        Args:
            persist_directory: Directory for persistent storage
        """
        self.persist_directory = persist_directory
        self.ensure_directory_exists(persist_directory)
        
        # Initialize ChromaDB
        self.chroma_client = self._init_chromadb()
        self.collections = {}
        
        # Initialize FAISS indexes
        self.faiss_indexes = {}
        self.faiss_metadata = {}
        
        # Initialize metadata store
        self.metadata_db_path = os.path.join(persist_directory, "metadata.db")
        self._init_metadata_db()
        
        logger.info("GameCockVectorDB initialized successfully")
    
    def _init_chromadb(self) -> chromadb.Client:
        """Initialize ChromaDB client with modern settings"""
        try:
            # Use modern ChromaDB configuration (v0.4.15+)
            client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True,
                    is_persistent=True
                )
            )
            logger.info("ChromaDB client initialized with modern settings")
            return client
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise
    
    def _init_metadata_db(self):
        """Initialize SQLite database for metadata storage"""
        try:
            conn = sqlite3.connect(self.metadata_db_path)
            cursor = conn.cursor()
            
            # Create metadata table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS vector_metadata (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    collection_name TEXT NOT NULL,
                    vector_id TEXT NOT NULL,
                    metadata_json TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_collection_vector ON vector_metadata(collection_name, vector_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON vector_metadata(created_at)")
            
            conn.commit()
            conn.close()
            logger.info("Metadata database initialized")
        except Exception as e:
            logger.error(f"Failed to initialize metadata database: {e}")
            raise
    
    def create_collection(self, 
                         name: str, 
                         embedding_function: Any = None,
                         collection_type: str = "chroma",
                         dimension: int = 768,
                         distance_metric: str = "cosine") -> bool:
        """
        Create a new vector collection
        
        Args:
            name: Collection name
            embedding_function: Function to generate embeddings
            collection_type: "chroma" or "faiss"
            dimension: Vector dimension for FAISS
            distance_metric: Distance metric for similarity search
            
        Returns:
            bool: Success status
        """
        try:
            if collection_type == "chroma":
                return self._create_chroma_collection(name, embedding_function, distance_metric)
            elif collection_type == "faiss":
                return self._create_faiss_collection(name, dimension, distance_metric)
            else:
                raise ValueError(f"Unsupported collection type: {collection_type}")
        except Exception as e:
            logger.error(f"Failed to create collection {name}: {e}")
            return False
    
    def _create_chroma_collection(self, name: str, embedding_function: Any, distance_metric: str) -> bool:
        """Create ChromaDB collection for document-level search"""
        try:
            # Check if collection already exists
            existing_collections = [col.name for col in self.chroma_client.list_collections()]
            if name in existing_collections:
                logger.info(f"Collection {name} already exists, loading existing")
                self.collections[name] = self.chroma_client.get_collection(name)
                return True
            
            # Configure distance metric
            metadata = {"hnsw:space": distance_metric}
            if distance_metric == "cosine":
                metadata.update({
                    "hnsw:construction_ef": 200,
                    "hnsw:M": 16,
                    "hnsw:search_ef": 100
                })
            
            # Create new collection
            collection = self.chroma_client.create_collection(
                name=name,
                embedding_function=embedding_function,
                metadata=metadata
            )
            
            self.collections[name] = collection
            logger.info(f"ChromaDB collection {name} created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create ChromaDB collection {name}: {e}")
            return False
    
    def _create_faiss_collection(self, name: str, dimension: int, distance_metric: str) -> bool:
        """Create FAISS index for high-performance numerical search"""
        try:
            # Choose FAISS index type based on distance metric
            if distance_metric == "cosine":
                # Normalize vectors for cosine similarity using L2 distance
                index = faiss.IndexFlatIP(dimension)  # Inner product for normalized vectors
            elif distance_metric == "l2":
                index = faiss.IndexFlatL2(dimension)
            elif distance_metric == "l1":
                index = faiss.IndexFlat(dimension, faiss.METRIC_L1)
            else:
                raise ValueError(f"Unsupported FAISS distance metric: {distance_metric}")
            
            # Store index and metadata
            self.faiss_indexes[name] = index
            self.faiss_metadata[name] = {
                "dimension": dimension,
                "distance_metric": distance_metric,
                "size": 0,
                "id_map": {},  # Maps internal FAISS IDs to external IDs
                "created_at": datetime.now().isoformat()
            }
            
            logger.info(f"FAISS collection {name} created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create FAISS collection {name}: {e}")
            return False
    
    def add_documents(self, 
                     collection_name: str,
                     documents: List[str],
                     metadatas: List[Dict[str, Any]],
                     ids: List[str],
                     embeddings: Optional[List[List[float]]] = None) -> bool:
        """
        Add documents to a ChromaDB collection
        
        Args:
            collection_name: Target collection name
            documents: List of document texts
            metadatas: List of metadata dictionaries
            ids: List of document IDs
            embeddings: Pre-computed embeddings (optional)
            
        Returns:
            bool: Success status
        """
        try:
            if collection_name not in self.collections:
                raise ValueError(f"Collection {collection_name} does not exist")
            
            collection = self.collections[collection_name]
            
            # Add documents to ChromaDB
            if embeddings:
                collection.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids,
                    embeddings=embeddings
                )
            else:
                collection.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )
            
            # Store metadata in SQLite
            self._store_metadata(collection_name, ids, metadatas)
            
            logger.info(f"Added {len(documents)} documents to collection {collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add documents to collection {collection_name}: {e}")
            return False
    
    def add_vectors(self,
                   collection_name: str,
                   vectors: np.ndarray,
                   ids: List[str],
                   metadatas: Optional[List[Dict[str, Any]]] = None) -> bool:
        """
        Add vectors to a FAISS collection
        
        Args:
            collection_name: Target collection name
            vectors: Vector array (n_vectors, dimension)
            ids: List of vector IDs
            metadatas: Optional metadata for each vector
            
        Returns:
            bool: Success status
        """
        try:
            if collection_name not in self.faiss_indexes:
                raise ValueError(f"FAISS collection {collection_name} does not exist")
            
            index = self.faiss_indexes[collection_name]
            metadata = self.faiss_metadata[collection_name]
            
            # Normalize vectors if using cosine similarity
            if metadata["distance_metric"] == "cosine":
                vectors_normalized = vectors / np.linalg.norm(vectors, axis=1, keepdims=True)
                index.add(vectors_normalized.astype(np.float32))
            else:
                index.add(vectors.astype(np.float32))
            
            # Update ID mapping
            start_idx = metadata["size"]
            for i, external_id in enumerate(ids):
                metadata["id_map"][start_idx + i] = external_id
            
            metadata["size"] += len(vectors)
            
            # Store metadata if provided
            if metadatas:
                self._store_metadata(collection_name, ids, metadatas)
            
            logger.info(f"Added {len(vectors)} vectors to FAISS collection {collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add vectors to FAISS collection {collection_name}: {e}")
            return False
    
    def query_documents(self,
                       collection_name: str,
                       query_texts: List[str] = None,
                       query_embeddings: List[List[float]] = None,
                       n_results: int = 10,
                       where: Optional[Dict[str, Any]] = None,
                       include: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Query documents from ChromaDB collection
        
        Args:
            collection_name: Collection to query
            query_texts: Query text strings
            query_embeddings: Pre-computed query embeddings
            n_results: Number of results to return
            where: Metadata filter conditions
            include: Fields to include in results
            
        Returns:
            Dict containing query results
        """
        try:
            if collection_name not in self.collections:
                raise ValueError(f"Collection {collection_name} does not exist")
            
            collection = self.collections[collection_name]
            
            # Set default include fields
            if include is None:
                include = ["documents", "metadatas", "distances"]
            
            # Perform query
            if query_texts:
                results = collection.query(
                    query_texts=query_texts,
                    n_results=n_results,
                    where=where,
                    include=include
                )
            elif query_embeddings:
                results = collection.query(
                    query_embeddings=query_embeddings,
                    n_results=n_results,
                    where=where,
                    include=include
                )
            else:
                raise ValueError("Either query_texts or query_embeddings must be provided")
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to query collection {collection_name}: {e}")
            return {"error": str(e)}
    
    def query_vectors(self,
                     collection_name: str,
                     query_vectors: np.ndarray,
                     k: int = 10) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """
        Query vectors from FAISS collection
        
        Args:
            collection_name: Collection to query
            query_vectors: Query vector array
            k: Number of nearest neighbors to return
            
        Returns:
            Tuple of (distances, indices, external_ids)
        """
        try:
            if collection_name not in self.faiss_indexes:
                raise ValueError(f"FAISS collection {collection_name} does not exist")
            
            index = self.faiss_indexes[collection_name]
            metadata = self.faiss_metadata[collection_name]
            
            # Normalize query vectors if using cosine similarity
            if metadata["distance_metric"] == "cosine":
                query_vectors_normalized = query_vectors / np.linalg.norm(query_vectors, axis=1, keepdims=True)
                distances, indices = index.search(query_vectors_normalized.astype(np.float32), k)
            else:
                distances, indices = index.search(query_vectors.astype(np.float32), k)
            
            # Map internal indices to external IDs
            external_ids = []
            for query_indices in indices:
                query_external_ids = []
                for idx in query_indices:
                    if idx != -1:  # Valid index
                        external_id = metadata["id_map"].get(idx, f"unknown_{idx}")
                        query_external_ids.append(external_id)
                    else:
                        query_external_ids.append(None)
                external_ids.append(query_external_ids)
            
            return distances, indices, external_ids
            
        except Exception as e:
            logger.error(f"Failed to query FAISS collection {collection_name}: {e}")
            return np.array([]), np.array([]), []
    
    def _store_metadata(self, collection_name: str, ids: List[str], metadatas: List[Dict[str, Any]]):
        """Store metadata in SQLite database"""
        try:
            conn = sqlite3.connect(self.metadata_db_path)
            cursor = conn.cursor()
            
            for id_, metadata in zip(ids, metadatas):
                cursor.execute("""
                    INSERT OR REPLACE INTO vector_metadata 
                    (collection_name, vector_id, metadata_json, updated_at)
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                """, (collection_name, id_, json.dumps(metadata)))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to store metadata: {e}")
    
    def get_metadata(self, collection_name: str, vector_ids: List[str]) -> List[Dict[str, Any]]:
        """Retrieve metadata for given vector IDs"""
        try:
            conn = sqlite3.connect(self.metadata_db_path)
            cursor = conn.cursor()
            
            placeholders = ",".join(["?" for _ in vector_ids])
            cursor.execute(f"""
                SELECT vector_id, metadata_json FROM vector_metadata
                WHERE collection_name = ? AND vector_id IN ({placeholders})
            """, [collection_name] + vector_ids)
            
            results = cursor.fetchall()
            conn.close()
            
            # Create metadata dictionary
            metadata_dict = {row[0]: json.loads(row[1]) for row in results}
            
            # Return metadata in same order as input IDs
            return [metadata_dict.get(id_, {}) for id_ in vector_ids]
            
        except Exception as e:
            logger.error(f"Failed to retrieve metadata: {e}")
            return [{} for _ in vector_ids]
    
    def get_collection_stats(self, collection_name: str) -> Dict[str, Any]:
        """Get statistics for a collection"""
        try:
            stats = {"collection_name": collection_name}
            
            if collection_name in self.collections:
                # ChromaDB stats
                collection = self.collections[collection_name]
                stats.update({
                    "type": "chromadb",
                    "count": collection.count(),
                    "name": collection.name
                })
            
            elif collection_name in self.faiss_indexes:
                # FAISS stats
                metadata = self.faiss_metadata[collection_name]
                stats.update({
                    "type": "faiss",
                    "count": metadata["size"],
                    "dimension": metadata["dimension"],
                    "distance_metric": metadata["distance_metric"]
                })
            
            else:
                stats["error"] = "Collection not found"
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {"error": str(e)}
    
    def list_collections(self) -> List[str]:
        """List all available collections"""
        collections = list(self.collections.keys()) + list(self.faiss_indexes.keys())
        return collections
    
    def save_faiss_indexes(self):
        """Save FAISS indexes to disk"""
        try:
            for name, index in self.faiss_indexes.items():
                index_path = os.path.join(self.persist_directory, f"{name}.faiss")
                metadata_path = os.path.join(self.persist_directory, f"{name}_metadata.pkl")
                
                # Save FAISS index
                faiss.write_index(index, index_path)
                
                # Save metadata
                with open(metadata_path, 'wb') as f:
                    pickle.dump(self.faiss_metadata[name], f)
            
            logger.info("FAISS indexes saved to disk")
            
        except Exception as e:
            logger.error(f"Failed to save FAISS indexes: {e}")
    
    def load_faiss_indexes(self):
        """Load FAISS indexes from disk"""
        try:
            for file in os.listdir(self.persist_directory):
                if file.endswith('.faiss'):
                    name = file[:-6]  # Remove .faiss extension
                    index_path = os.path.join(self.persist_directory, file)
                    metadata_path = os.path.join(self.persist_directory, f"{name}_metadata.pkl")
                    
                    # Load FAISS index
                    index = faiss.read_index(index_path)
                    self.faiss_indexes[name] = index
                    
                    # Load metadata
                    if os.path.exists(metadata_path):
                        with open(metadata_path, 'rb') as f:
                            self.faiss_metadata[name] = pickle.load(f)
                    else:
                        logger.warning(f"Metadata file not found for {name}")
            
            logger.info("FAISS indexes loaded from disk")
            
        except Exception as e:
            logger.error(f"Failed to load FAISS indexes: {e}")
    
    @staticmethod
    def ensure_directory_exists(directory: str):
        """Ensure directory exists, create if it doesn't"""
        if not os.path.exists(directory):
            os.makedirs(directory)
            logger.info(f"Created directory: {directory}")
    
    def close(self):
        """Clean up resources"""
        try:
            # Save FAISS indexes before closing
            self.save_faiss_indexes()
            logger.info("Vector database closed successfully")
        except Exception as e:
            logger.error(f"Error closing vector database: {e}")


class VectorDBManager:
    """
    High-level manager for GameCock vector database operations
    Provides simplified interface for common operations
    """
    
    def __init__(self, persist_directory: str = "./vector_store"):
        self.db = GameCockVectorDB(persist_directory)
        self._initialize_standard_collections()
    
    def _initialize_standard_collections(self):
        """Initialize standard collections for GameCock data types"""
        
        # Document collections (ChromaDB)
        document_collections = [
            "sec_filings",
            "cftc_summaries", 
            "insider_reports",
            "form_d_filings",
            "fund_reports",
            "market_events",
            "risk_assessments"
        ]
        
        for collection in document_collections:
            self.db.create_collection(
                name=collection,
                collection_type="chroma",
                distance_metric="cosine"
            )
        
        # Numerical data collections (FAISS)
        numerical_collections = [
            ("cftc_numerical", 768),
            ("market_indicators", 512), 
            ("company_profiles", 1024)
        ]
        
        for collection, dimension in numerical_collections:
            self.db.create_collection(
                name=collection,
                collection_type="faiss",
                dimension=dimension,
                distance_metric="cosine"
            )
    
    def add_sec_filing(self, 
                      filing_id: str,
                      content: str,
                      metadata: Dict[str, Any],
                      embeddings: Optional[List[float]] = None):
        """Add SEC filing to appropriate collection"""
        return self.db.add_documents(
            collection_name="sec_filings",
            documents=[content],
            metadatas=[metadata],
            ids=[filing_id],
            embeddings=[embeddings] if embeddings else None
        )
    
    def add_cftc_summary(self,
                        summary_id: str,
                        content: str,
                        metadata: Dict[str, Any],
                        embeddings: Optional[List[float]] = None):
        """Add CFTC summary to appropriate collection"""
        return self.db.add_documents(
            collection_name="cftc_summaries",
            documents=[content],
            metadatas=[metadata],
            ids=[summary_id],
            embeddings=[embeddings] if embeddings else None
        )
    
    def semantic_search(self,
                       query: str,
                       collection_names: List[str] = None,
                       n_results: int = 10,
                       filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Perform semantic search across specified collections
        
        Args:
            query: Search query text
            collection_names: Collections to search (default: all document collections)
            n_results: Number of results per collection
            filters: Metadata filters
            
        Returns:
            Aggregated search results
        """
        if collection_names is None:
            collection_names = ["sec_filings", "cftc_summaries", "insider_reports", "form_d_filings"]
        
        all_results = {}
        
        for collection_name in collection_names:
            if collection_name in self.db.collections:
                results = self.db.query_documents(
                    collection_name=collection_name,
                    query_texts=[query],
                    n_results=n_results,
                    where=filters
                )
                all_results[collection_name] = results
        
        return all_results
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics"""
        stats = {
            "collections": {},
            "total_documents": 0,
            "total_vectors": 0
        }
        
        for collection_name in self.db.list_collections():
            collection_stats = self.db.get_collection_stats(collection_name)
            stats["collections"][collection_name] = collection_stats
            
            if collection_stats.get("type") == "chromadb":
                stats["total_documents"] += collection_stats.get("count", 0)
            elif collection_stats.get("type") == "faiss":
                stats["total_vectors"] += collection_stats.get("count", 0)
        
        return stats

