"""
Document Processing Pipeline for GameCock AI Vector Embeddings
Handles intelligent chunking and preprocessing of financial documents
"""

import re
import json
import tiktoken
import numpy as np
from typing import List, Dict, Any, Tuple, Optional, Union
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
from enum import Enum
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import hashlib

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentType(Enum):
    """Enumeration of supported document types"""
    SEC_10K = "10-K"
    SEC_10Q = "10-Q"
    SEC_8K = "8-K"
    SEC_INSIDER = "INSIDER"
    FORM_13F = "13F"
    FORM_D = "FORM_D"
    N_MFP = "N-MFP"
    N_CEN = "N-CEN"
    N_PORT = "N-PORT"
    CFTC_SWAP = "CFTC_SWAP"
    EXCHANGE_DATA = "EXCHANGE"
    GENERAL = "GENERAL"

@dataclass
class DocumentChunk:
    """Represents a processed document chunk with metadata"""
    chunk_id: str
    content: str
    metadata: Dict[str, Any]
    chunk_type: str
    source_document: str
    start_position: int
    end_position: int
    token_count: int
    importance_score: float = 0.0

@dataclass
class ProcessingResult:
    """Result of document processing operation"""
    chunks: List[DocumentChunk]
    metadata: Dict[str, Any]
    processing_stats: Dict[str, Any]
    errors: List[str] = None

class FinancialDocumentProcessor:
    """
    Advanced document processor for financial documents
    Handles intelligent chunking, section extraction, and metadata enhancement
    """
    
    def __init__(self, 
                 max_chunk_size: int = 512,
                 overlap_size: int = 50,
                 min_chunk_size: int = 100,
                 preserve_structure: bool = True):
        """
        Initialize the document processor
        
        Args:
            max_chunk_size: Maximum tokens per chunk
            overlap_size: Overlap between consecutive chunks
            min_chunk_size: Minimum tokens per chunk
            preserve_structure: Whether to preserve document structure
        """
        self.max_chunk_size = max_chunk_size
        self.overlap_size = overlap_size
        self.min_chunk_size = min_chunk_size
        self.preserve_structure = preserve_structure
        
        # Initialize tokenizer
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
        
        # Financial concept patterns
        self._init_financial_patterns()
        
        # SEC section patterns
        self._init_sec_patterns()
        
        logger.info("FinancialDocumentProcessor initialized")
    
    def _init_financial_patterns(self):
        """Initialize patterns for financial concept detection"""
        self.financial_patterns = {
            'risk_indicators': [
                r'risk\s+factor', r'material\s+risk', r'significant\s+risk',
                r'credit\s+risk', r'market\s+risk', r'operational\s+risk',
                r'liquidity\s+risk', r'regulatory\s+risk', r'cyber\s+risk'
            ],
            'financial_metrics': [
                r'revenue', r'net\s+income', r'earnings', r'profit',
                r'cash\s+flow', r'ebitda', r'assets', r'liabilities',
                r'debt', r'equity', r'dividend', r'market\s+cap'
            ],
            'business_segments': [
                r'business\s+segment', r'operating\s+segment', r'division',
                r'subsidiary', r'acquisition', r'merger', r'joint\s+venture'
            ],
            'regulatory_terms': [
                r'sec\s+filing', r'compliance', r'regulation', r'regulatory',
                r'sox\s+compliance', r'internal\s+control', r'audit'
            ],
            'market_terms': [
                r'market\s+share', r'competition', r'competitive',
                r'industry', r'sector', r'market\s+condition'
            ]
        }
    
    def _init_sec_patterns(self):
        """Initialize patterns for SEC document section extraction"""
        self.sec_section_patterns = {
            'business': [
                r'item\s+1\.\s*business',
                r'part\s+i.*item\s+1\s*business',
                r'description\s+of\s+business'
            ],
            'risk_factors': [
                r'item\s+1a\.\s*risk\s+factors',
                r'part\s+i.*item\s+1a\s*risk\s+factors',
                r'risk\s+factors'
            ],
            'properties': [
                r'item\s+2\.\s*properties',
                r'part\s+i.*item\s+2\s*properties'
            ],
            'legal_proceedings': [
                r'item\s+3\.\s*legal\s+proceedings',
                r'part\s+i.*item\s+3\s*legal\s+proceedings'
            ],
            'controls': [
                r'item\s+9a\.\s*controls\s+and\s+procedures',
                r'controls\s+and\s+procedures'
            ],
            'financial_statements': [
                r'item\s+8\.\s*financial\s+statements',
                r'consolidated\s+financial\s+statements',
                r'financial\s+statements\s+and\s+supplementary\s+data'
            ],
            'management_discussion': [
                r'item\s+7\.\s*management\'s\s+discussion',
                r'md&a',
                r'management\s+discussion\s+and\s+analysis'
            ]
        }
    
    def process_document(self, 
                        document_text: str,
                        document_type: DocumentType,
                        metadata: Dict[str, Any] = None) -> ProcessingResult:
        """
        Process a financial document into optimized chunks
        
        Args:
            document_text: Raw document text
            document_type: Type of document being processed
            metadata: Additional metadata about the document
            
        Returns:
            ProcessingResult with chunks and metadata
        """
        try:
            start_time = datetime.now()
            
            if metadata is None:
                metadata = {}
            
            # Clean and preprocess the document
            cleaned_text = self._clean_document_text(document_text)
            
            # Extract document structure if applicable
            if document_type in [DocumentType.SEC_10K, DocumentType.SEC_10Q, DocumentType.SEC_8K]:
                sections = self._extract_sec_sections(cleaned_text)
            else:
                sections = {"main": cleaned_text}
            
            # Generate chunks based on document type
            all_chunks = []
            errors = []
            
            for section_name, section_text in sections.items():
                try:
                    section_chunks = self._create_chunks(
                        section_text, 
                        document_type, 
                        section_name,
                        metadata
                    )
                    all_chunks.extend(section_chunks)
                except Exception as e:
                    error_msg = f"Failed to process section {section_name}: {str(e)}"
                    logger.error(error_msg)
                    errors.append(error_msg)
            
            # Calculate importance scores
            all_chunks = self._calculate_importance_scores(all_chunks, document_type)
            
            # Generate processing statistics
            processing_time = (datetime.now() - start_time).total_seconds()
            stats = {
                "processing_time_seconds": processing_time,
                "original_length": len(document_text),
                "cleaned_length": len(cleaned_text),
                "total_chunks": len(all_chunks),
                "sections_processed": len(sections),
                "average_chunk_size": np.mean([chunk.token_count for chunk in all_chunks]) if all_chunks else 0,
                "min_chunk_size": min([chunk.token_count for chunk in all_chunks]) if all_chunks else 0,
                "max_chunk_size": max([chunk.token_count for chunk in all_chunks]) if all_chunks else 0
            }
            
            return ProcessingResult(
                chunks=all_chunks,
                metadata=metadata,
                processing_stats=stats,
                errors=errors if errors else None
            )
            
        except Exception as e:
            logger.error(f"Document processing failed: {str(e)}")
            return ProcessingResult(
                chunks=[],
                metadata=metadata or {},
                processing_stats={"error": str(e)},
                errors=[str(e)]
            )
    
    def _clean_document_text(self, text: str) -> str:
        """Clean and normalize document text"""
        # Remove HTML tags if present
        if '<' in text and '>' in text:
            soup = BeautifulSoup(text, 'html.parser')
            text = soup.get_text()
        
        # Remove XML tags if present
        text = re.sub(r'<[^>]+>', '', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        # Remove page numbers and headers/footers
        text = re.sub(r'page\s+\d+\s+of\s+\d+', '', text, flags=re.IGNORECASE)
        text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)
        
        # Fix common encoding issues
        text = text.replace('\xa0', ' ')  # Non-breaking space
        text = text.replace('\u2019', "'")  # Right single quotation mark
        text = text.replace('\u201c', '"')  # Left double quotation mark
        text = text.replace('\u201d', '"')  # Right double quotation mark
        
        # Remove excessive punctuation
        text = re.sub(r'[\.]{3,}', '...', text)
        text = re.sub(r'[-]{3,}', '---', text)
        
        return text.strip()
    
    def _extract_sec_sections(self, text: str) -> Dict[str, str]:
        """Extract sections from SEC documents"""
        sections = {}
        text_lower = text.lower()
        
        # Find section boundaries
        section_boundaries = []
        
        for section_name, patterns in self.sec_section_patterns.items():
            for pattern in patterns:
                matches = list(re.finditer(pattern, text_lower, re.IGNORECASE))
                for match in matches:
                    section_boundaries.append((match.start(), section_name, match.group()))
        
        # Sort boundaries by position
        section_boundaries.sort(key=lambda x: x[0])
        
        # Extract section text
        for i, (start_pos, section_name, match_text) in enumerate(section_boundaries):
            # Determine end position
            if i + 1 < len(section_boundaries):
                end_pos = section_boundaries[i + 1][0]
            else:
                end_pos = len(text)
            
            # Extract section content
            section_text = text[start_pos:end_pos].strip()
            
            # Skip very short sections
            if len(section_text) > self.min_chunk_size:
                sections[section_name] = section_text
        
        # If no sections found, treat entire document as main section
        if not sections:
            sections["main"] = text
        
        return sections
    
    def _create_chunks(self, 
                      text: str, 
                      document_type: DocumentType,
                      section_name: str,
                      base_metadata: Dict[str, Any]) -> List[DocumentChunk]:
        """Create optimized chunks from text"""
        chunks = []
        
        if document_type in [DocumentType.SEC_10K, DocumentType.SEC_10Q, DocumentType.SEC_8K]:
            chunks = self._create_sec_chunks(text, section_name, base_metadata)
        elif document_type == DocumentType.CFTC_SWAP:
            chunks = self._create_cftc_chunks(text, base_metadata)
        elif document_type in [DocumentType.FORM_13F, DocumentType.FORM_D]:
            chunks = self._create_form_chunks(text, document_type, base_metadata)
        else:
            chunks = self._create_generic_chunks(text, section_name, base_metadata)
        
        return chunks
    
    def _create_sec_chunks(self, 
                          text: str, 
                          section_name: str,
                          base_metadata: Dict[str, Any]) -> List[DocumentChunk]:
        """Create chunks optimized for SEC filings"""
        chunks = []
        
        # Split text into paragraphs
        paragraphs = self._split_into_paragraphs(text)
        
        current_chunk = ""
        current_tokens = 0
        chunk_index = 0
        start_position = 0
        
        for para_index, paragraph in enumerate(paragraphs):
            para_tokens = len(self.tokenizer.encode(paragraph))
            
            # Check if paragraph fits in current chunk
            if current_tokens + para_tokens <= self.max_chunk_size:
                current_chunk += paragraph + "\n\n"
                current_tokens += para_tokens
            else:
                # Finalize current chunk if it has content
                if current_chunk.strip() and current_tokens >= self.min_chunk_size:
                    chunk = self._create_chunk(
                        current_chunk.strip(),
                        f"sec_{section_name}_{chunk_index}",
                        f"sec_{section_name}",
                        base_metadata,
                        start_position,
                        start_position + len(current_chunk)
                    )
                    chunks.append(chunk)
                    chunk_index += 1
                
                # Start new chunk
                start_position += len(current_chunk)
                current_chunk = paragraph + "\n\n"
                current_tokens = para_tokens
        
        # Add final chunk
        if current_chunk.strip() and current_tokens >= self.min_chunk_size:
            chunk = self._create_chunk(
                current_chunk.strip(),
                f"sec_{section_name}_{chunk_index}",
                f"sec_{section_name}",
                base_metadata,
                start_position,
                start_position + len(current_chunk)
            )
            chunks.append(chunk)
        
        return chunks
    
    def _create_cftc_chunks(self, 
                           text: str,
                           base_metadata: Dict[str, Any]) -> List[DocumentChunk]:
        """Create chunks optimized for CFTC swap data"""
        chunks = []
        
        # CFTC data is typically structured, so we split by transactions or logical units
        lines = text.strip().split('\n')
        
        current_chunk_lines = []
        current_tokens = 0
        chunk_index = 0
        
        for line in lines:
            line_tokens = len(self.tokenizer.encode(line))
            
            if current_tokens + line_tokens <= self.max_chunk_size:
                current_chunk_lines.append(line)
                current_tokens += line_tokens
            else:
                # Finalize current chunk
                if current_chunk_lines and current_tokens >= self.min_chunk_size:
                    chunk_text = '\n'.join(current_chunk_lines)
                    chunk = self._create_chunk(
                        chunk_text,
                        f"cftc_swap_{chunk_index}",
                        "cftc_swap_data",
                        base_metadata,
                        0,  # Position tracking less relevant for structured data
                        len(chunk_text)
                    )
                    chunks.append(chunk)
                    chunk_index += 1
                
                # Start new chunk
                current_chunk_lines = [line]
                current_tokens = line_tokens
        
        # Add final chunk
        if current_chunk_lines and current_tokens >= self.min_chunk_size:
            chunk_text = '\n'.join(current_chunk_lines)
            chunk = self._create_chunk(
                chunk_text,
                f"cftc_swap_{chunk_index}",
                "cftc_swap_data",
                base_metadata,
                0,
                len(chunk_text)
            )
            chunks.append(chunk)
        
        return chunks
    
    def _create_form_chunks(self, 
                           text: str,
                           document_type: DocumentType,
                           base_metadata: Dict[str, Any]) -> List[DocumentChunk]:
        """Create chunks for Form 13F, Form D, etc."""
        chunks = []
        
        # Forms often have structured sections, split by logical boundaries
        sections = self._split_form_sections(text, document_type)
        
        chunk_index = 0
        for section_name, section_text in sections.items():
            section_chunks = self._sliding_window_chunk(
                section_text,
                f"{document_type.value.lower()}_{section_name}_{chunk_index}",
                f"{document_type.value.lower()}_{section_name}",
                base_metadata
            )
            chunks.extend(section_chunks)
            chunk_index += len(section_chunks)
        
        return chunks
    
    def _create_generic_chunks(self, 
                              text: str,
                              section_name: str,
                              base_metadata: Dict[str, Any]) -> List[DocumentChunk]:
        """Create chunks for generic documents"""
        return self._sliding_window_chunk(
            text,
            f"generic_{section_name}",
            f"generic_{section_name}",
            base_metadata
        )
    
    def _sliding_window_chunk(self, 
                             text: str,
                             chunk_id_prefix: str,
                             chunk_type: str,
                             base_metadata: Dict[str, Any]) -> List[DocumentChunk]:
        """Create chunks using sliding window approach"""
        chunks = []
        tokens = self.tokenizer.encode(text)
        
        if len(tokens) <= self.max_chunk_size:
            # Text fits in one chunk
            chunk = self._create_chunk(
                text,
                f"{chunk_id_prefix}_0",
                chunk_type,
                base_metadata,
                0,
                len(text)
            )
            chunks.append(chunk)
        else:
            # Split into overlapping chunks
            chunk_index = 0
            start_token = 0
            
            while start_token < len(tokens):
                # Determine chunk boundaries
                end_token = min(start_token + self.max_chunk_size, len(tokens))
                chunk_tokens = tokens[start_token:end_token]
                
                # Decode tokens back to text
                chunk_text = self.tokenizer.decode(chunk_tokens)
                
                # Create chunk
                chunk = self._create_chunk(
                    chunk_text,
                    f"{chunk_id_prefix}_{chunk_index}",
                    chunk_type,
                    base_metadata,
                    start_token,
                    end_token
                )
                chunks.append(chunk)
                
                # Move to next chunk with overlap
                start_token = end_token - self.overlap_size
                chunk_index += 1
                
                # Prevent infinite loop
                if start_token >= len(tokens) - self.min_chunk_size:
                    break
        
        return chunks
    
    def _create_chunk(self, 
                     text: str,
                     chunk_id: str,
                     chunk_type: str,
                     base_metadata: Dict[str, Any],
                     start_position: int,
                     end_position: int) -> DocumentChunk:
        """Create a DocumentChunk with enhanced metadata"""
        
        # Count tokens
        token_count = len(self.tokenizer.encode(text))
        
        # Enhance metadata with content analysis
        enhanced_metadata = base_metadata.copy()
        enhanced_metadata.update({
            'token_count': token_count,
            'character_count': len(text),
            'financial_concepts': self._extract_financial_concepts(text),
            'contains_numbers': bool(re.search(r'\d', text)),
            'contains_currency': bool(re.search(r'\$|USD|currency|dollar', text, re.IGNORECASE)),
            'risk_indicators': self._count_risk_indicators(text),
            'readability_score': self._calculate_readability_score(text),
            'created_at': datetime.now().isoformat()
        })
        
        return DocumentChunk(
            chunk_id=chunk_id,
            content=text,
            metadata=enhanced_metadata,
            chunk_type=chunk_type,
            source_document=base_metadata.get('document_id', 'unknown'),
            start_position=start_position,
            end_position=end_position,
            token_count=token_count
        )
    
    def _split_into_paragraphs(self, text: str) -> List[str]:
        """Split text into logical paragraphs"""
        # Split on double newlines first
        paragraphs = re.split(r'\n\s*\n', text)
        
        # Further split very long paragraphs
        result = []
        for para in paragraphs:
            if len(self.tokenizer.encode(para)) > self.max_chunk_size:
                # Split long paragraph by sentences
                sentences = re.split(r'(?<=[.!?])\s+', para)
                current_para = ""
                
                for sentence in sentences:
                    test_para = current_para + " " + sentence if current_para else sentence
                    if len(self.tokenizer.encode(test_para)) <= self.max_chunk_size:
                        current_para = test_para
                    else:
                        if current_para:
                            result.append(current_para)
                        current_para = sentence
                
                if current_para:
                    result.append(current_para)
            else:
                result.append(para)
        
        return [p.strip() for p in result if p.strip()]
    
    def _split_form_sections(self, text: str, document_type: DocumentType) -> Dict[str, str]:
        """Split form documents into logical sections"""
        sections = {"main": text}  # Default fallback
        
        if document_type == DocumentType.FORM_13F:
            # Common 13F sections
            section_patterns = {
                'summary': r'summary\s+page',
                'holdings': r'(holdings|securities|positions)',
                'other_info': r'other\s+information'
            }
        elif document_type == DocumentType.FORM_D:
            # Common Form D sections
            section_patterns = {
                'issuer': r'issuer\s+information',
                'offering': r'offering\s+information',
                'investors': r'investor\s+information'
            }
        else:
            return sections
        
        # Extract sections based on patterns
        text_lower = text.lower()
        found_sections = {}
        
        for section_name, pattern in section_patterns.items():
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                start_pos = match.start()
                found_sections[section_name] = start_pos
        
        # If sections found, split text accordingly
        if found_sections:
            sorted_sections = sorted(found_sections.items(), key=lambda x: x[1])
            sections = {}
            
            for i, (section_name, start_pos) in enumerate(sorted_sections):
                if i + 1 < len(sorted_sections):
                    end_pos = sorted_sections[i + 1][1]
                else:
                    end_pos = len(text)
                
                section_text = text[start_pos:end_pos].strip()
                if len(section_text) > self.min_chunk_size:
                    sections[section_name] = section_text
        
        return sections
    
    def _extract_financial_concepts(self, text: str) -> List[str]:
        """Extract financial concepts from text"""
        concepts = []
        text_lower = text.lower()
        
        for category, patterns in self.financial_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    concepts.append(category)
                    break  # Avoid duplicates for the same category
        
        return concepts
    
    def _count_risk_indicators(self, text: str) -> int:
        """Count risk-related terms in text"""
        risk_count = 0
        text_lower = text.lower()
        
        for pattern in self.financial_patterns['risk_indicators']:
            matches = re.findall(pattern, text_lower)
            risk_count += len(matches)
        
        return risk_count
    
    def _calculate_readability_score(self, text: str) -> float:
        """Calculate a simple readability score"""
        if not text:
            return 0.0
        
        # Count sentences, words, and syllables (simplified)
        sentences = len(re.findall(r'[.!?]+', text))
        words = len(re.findall(r'\w+', text))
        
        if sentences == 0 or words == 0:
            return 0.0
        
        # Simplified Flesch formula
        avg_sentence_length = words / sentences
        score = 206.835 - (1.015 * avg_sentence_length)
        
        # Normalize to 0-1 range
        return max(0.0, min(1.0, score / 100.0))
    
    def _calculate_importance_scores(self, 
                                   chunks: List[DocumentChunk],
                                   document_type: DocumentType) -> List[DocumentChunk]:
        """Calculate importance scores for chunks"""
        
        for chunk in chunks:
            score = 0.0
            
            # Base score from chunk type
            if 'risk' in chunk.chunk_type.lower():
                score += 0.3
            elif 'business' in chunk.chunk_type.lower():
                score += 0.2
            elif 'financial' in chunk.chunk_type.lower():
                score += 0.25
            
            # Score from financial concepts
            concept_count = len(chunk.metadata.get('financial_concepts', []))
            score += min(0.3, concept_count * 0.1)
            
            # Score from risk indicators
            risk_count = chunk.metadata.get('risk_indicators', 0)
            score += min(0.2, risk_count * 0.05)
            
            # Score from content characteristics
            if chunk.metadata.get('contains_currency', False):
                score += 0.1
            if chunk.metadata.get('contains_numbers', False):
                score += 0.05
            
            # Normalize score
            chunk.importance_score = min(1.0, score)
        
        return chunks
    
    def batch_process_documents(self, 
                               documents: List[Tuple[str, DocumentType, Dict[str, Any]]],
                               progress_callback: Optional[callable] = None) -> List[ProcessingResult]:
        """
        Process multiple documents in batch
        
        Args:
            documents: List of (text, document_type, metadata) tuples
            progress_callback: Optional callback for progress updates
            
        Returns:
            List of ProcessingResult objects
        """
        results = []
        
        for i, (text, doc_type, metadata) in enumerate(documents):
            try:
                result = self.process_document(text, doc_type, metadata)
                results.append(result)
                
                if progress_callback:
                    progress_callback(i + 1, len(documents), result)
                    
            except Exception as e:
                logger.error(f"Failed to process document {i}: {str(e)}")
                error_result = ProcessingResult(
                    chunks=[],
                    metadata=metadata or {},
                    processing_stats={"error": str(e)},
                    errors=[str(e)]
                )
                results.append(error_result)
        
        return results
    
    def get_processing_stats(self, results: List[ProcessingResult]) -> Dict[str, Any]:
        """Generate comprehensive processing statistics"""
        if not results:
            return {"error": "No results to analyze"}
        
        total_chunks = sum(len(result.chunks) for result in results)
        successful_docs = sum(1 for result in results if not result.errors)
        
        chunk_sizes = []
        importance_scores = []
        
        for result in results:
            for chunk in result.chunks:
                chunk_sizes.append(chunk.token_count)
                importance_scores.append(chunk.importance_score)
        
        stats = {
            "total_documents": len(results),
            "successful_documents": successful_docs,
            "failed_documents": len(results) - successful_docs,
            "total_chunks": total_chunks,
            "average_chunks_per_document": total_chunks / len(results) if results else 0,
            "chunk_size_stats": {
                "mean": np.mean(chunk_sizes) if chunk_sizes else 0,
                "median": np.median(chunk_sizes) if chunk_sizes else 0,
                "std": np.std(chunk_sizes) if chunk_sizes else 0,
                "min": np.min(chunk_sizes) if chunk_sizes else 0,
                "max": np.max(chunk_sizes) if chunk_sizes else 0
            },
            "importance_score_stats": {
                "mean": np.mean(importance_scores) if importance_scores else 0,
                "median": np.median(importance_scores) if importance_scores else 0,
                "high_importance_chunks": sum(1 for score in importance_scores if score > 0.7)
            }
        }
        
        return stats


class DocumentIndexer:
    """
    Utility class for creating searchable indexes of processed documents
    """
    
    def __init__(self, index_file: str = "document_index.json"):
        self.index_file = index_file
        self.index = self._load_index()
    
    def _load_index(self) -> Dict[str, Any]:
        """Load existing index from file"""
        try:
            with open(self.index_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "documents": {},
                "chunks": {},
                "metadata": {"created_at": datetime.now().isoformat()}
            }
    
    def add_processing_result(self, result: ProcessingResult, document_id: str):
        """Add processing result to index"""
        self.index["documents"][document_id] = {
            "chunk_count": len(result.chunks),
            "processing_stats": result.processing_stats,
            "metadata": result.metadata,
            "errors": result.errors
        }
        
        for chunk in result.chunks:
            self.index["chunks"][chunk.chunk_id] = {
                "document_id": document_id,
                "chunk_type": chunk.chunk_type,
                "token_count": chunk.token_count,
                "importance_score": chunk.importance_score,
                "metadata": chunk.metadata
            }
    
    def save_index(self):
        """Save index to file"""
        with open(self.index_file, 'w') as f:
            json.dump(self.index, f, indent=2)
    
    def search_chunks(self, 
                     query_terms: List[str],
                     min_importance: float = 0.0,
                     chunk_types: List[str] = None) -> List[str]:
        """Search for relevant chunk IDs based on criteria"""
        matching_chunks = []
        
        for chunk_id, chunk_info in self.index["chunks"].items():
            # Check importance threshold
            if chunk_info["importance_score"] < min_importance:
                continue
            
            # Check chunk types
            if chunk_types and chunk_info["chunk_type"] not in chunk_types:
                continue
            
            # Check query terms in metadata
            metadata_text = json.dumps(chunk_info["metadata"]).lower()
            if any(term.lower() in metadata_text for term in query_terms):
                matching_chunks.append(chunk_id)
        
        return matching_chunks

