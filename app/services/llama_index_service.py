import logging
import os
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
import tempfile

try:
    from llama_index.core import (
        VectorStoreIndex, 
        Document, 
        ServiceContext,
        StorageContext,
        load_index_from_storage
    )
    from llama_index.core.readers import SimpleDirectoryReader
    from llama_index.core.node_parser import SentenceSplitter
    from llama_index.core.storage.storage_context import DEFAULT_PERSIST_DIR
    from llama_index.core.query_engine import RetrieverQueryEngine
    from llama_index.core.retrievers import VectorIndexRetriever
    from llama_index.readers.file import PDFReader, DocxReader
    LLAMA_INDEX_AVAILABLE = True
except ImportError:
    logger = logging.getLogger(__name__)
    logger.warning("LlamaIndex not available - document processing features will be limited")
    LLAMA_INDEX_AVAILABLE = False

from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


class DocumentProcessingResult:
    """Result of document processing operation"""
    def __init__(self, success: bool, message: str, document_count: int = 0, error: str = None):
        self.success = success
        self.message = message
        self.document_count = document_count
        self.error = error


class SearchResult:
    """Result of document search operation"""
    def __init__(self, success: bool, query: str, results: List[Dict[str, Any]] = None, error: str = None):
        self.success = success
        self.query = query
        self.results = results or []
        self.error = error


class LlamaIndexService:
    """Service for document ingestion and search using LlamaIndex"""
    
    def __init__(self, persist_dir: str = "./data/index_storage"):
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        
        if not LLAMA_INDEX_AVAILABLE:
            logger.warning("LlamaIndex not available - service will run in limited mode")
            return
            
        self.index: Optional[VectorStoreIndex] = None
        self.query_engine = None
        self._initialize_index()
    
    def _initialize_index(self):
        """Initialize or load existing index"""
        if not LLAMA_INDEX_AVAILABLE:
            return
            
        try:
            # Try to load existing index
            if self.persist_dir.exists() and any(self.persist_dir.iterdir()):
                storage_context = StorageContext.from_defaults(persist_dir=str(self.persist_dir))
                self.index = load_index_from_storage(storage_context)
                logger.info("Loaded existing document index")
            else:
                # Create new empty index
                self.index = VectorStoreIndex([])
                logger.info("Created new document index")
                
            # Set up query engine
            self.query_engine = self.index.as_query_engine(
                similarity_top_k=5,
                response_mode="compact"
            )
            
        except Exception as e:
            logger.error(f"Failed to initialize LlamaIndex: {e}")
            self.index = None
    
    def ingest_documents(self, file_paths: List[Union[str, Path]], **kwargs) -> DocumentProcessingResult:
        """Ingest documents from file paths"""
        if not LLAMA_INDEX_AVAILABLE:
            return DocumentProcessingResult(
                success=False,
                error="LlamaIndex not available - please install llama-index package"
            )
            
        try:
            documents = []
            
            for file_path in file_paths:
                path = Path(file_path)
                if not path.exists():
                    logger.warning(f"File not found: {path}")
                    continue
                
                # Read document based on file type
                if path.suffix.lower() == '.pdf':
                    reader = PDFReader()
                    docs = reader.load_data(path)
                elif path.suffix.lower() == '.docx':
                    reader = DocxReader()
                    docs = reader.load_data(path)
                else:
                    # Use simple directory reader for other files
                    reader = SimpleDirectoryReader(input_files=[str(path)])
                    docs = reader.load_data()
                
                documents.extend(docs)
            
            if not documents:
                return DocumentProcessingResult(
                    success=False,
                    error="No valid documents found to ingest"
                )
            
            # Add documents to index
            if self.index is None:
                self.index = VectorStoreIndex.from_documents(documents)
            else:
                for doc in documents:
                    self.index.insert(doc)
            
            # Persist the index
            self.index.storage_context.persist(persist_dir=str(self.persist_dir))
            
            # Update query engine
            self.query_engine = self.index.as_query_engine(
                similarity_top_k=5,
                response_mode="compact"
            )
            
            logger.info(f"Successfully ingested {len(documents)} documents")
            return DocumentProcessingResult(
                success=True,
                message=f"Successfully ingested {len(documents)} documents",
                document_count=len(documents)
            )
            
        except Exception as e:
            logger.error(f"Error ingesting documents: {e}")
            return DocumentProcessingResult(
                success=False,
                error=str(e)
            )
    
    def ingest_text_documents(self, texts: List[str], metadata: List[Dict[str, Any]] = None) -> DocumentProcessingResult:
        """Ingest text documents directly"""
        if not LLAMA_INDEX_AVAILABLE:
            return DocumentProcessingResult(
                success=False,
                error="LlamaIndex not available - please install llama-index package"
            )
            
        try:
            documents = []
            metadata = metadata or [{}] * len(texts)
            
            for i, text in enumerate(texts):
                doc_metadata = metadata[i] if i < len(metadata) else {}
                doc = Document(text=text, metadata=doc_metadata)
                documents.append(doc)
            
            # Add documents to index
            if self.index is None:
                self.index = VectorStoreIndex.from_documents(documents)
            else:
                for doc in documents:
                    self.index.insert(doc)
            
            # Persist the index
            self.index.storage_context.persist(persist_dir=str(self.persist_dir))
            
            # Update query engine
            self.query_engine = self.index.as_query_engine(
                similarity_top_k=5,
                response_mode="compact"
            )
            
            logger.info(f"Successfully ingested {len(documents)} text documents")
            return DocumentProcessingResult(
                success=True,
                message=f"Successfully ingested {len(documents)} text documents",
                document_count=len(documents)
            )
            
        except Exception as e:
            logger.error(f"Error ingesting text documents: {e}")
            return DocumentProcessingResult(
                success=False,
                error=str(e)
            )
    
    def search_documents(self, query: str, top_k: int = 5) -> SearchResult:
        """Search through ingested documents"""
        if not LLAMA_INDEX_AVAILABLE:
            return SearchResult(
                success=False,
                query=query,
                error="LlamaIndex not available - please install llama-index package"
            )
            
        if not self.query_engine:
            return SearchResult(
                success=False,
                query=query,
                error="No documents have been ingested yet"
            )
        
        try:
            # Perform the search
            response = self.query_engine.query(query)
            
            # Extract results
            results = [{
                "text": str(response),
                "score": getattr(response, 'score', None),
                "metadata": getattr(response, 'metadata', {})
            }]
            
            # If we have source nodes, extract them
            if hasattr(response, 'source_nodes') and response.source_nodes:
                results = []
                for node in response.source_nodes[:top_k]:
                    results.append({
                        "text": node.text,
                        "score": node.score if hasattr(node, 'score') else None,
                        "metadata": node.metadata
                    })
            
            logger.info(f"Search query '{query}' returned {len(results)} results")
            return SearchResult(
                success=True,
                query=query,
                results=results
            )
            
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return SearchResult(
                success=False,
                query=query,
                error=str(e)
            )
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Get statistics about the current index"""
        if not LLAMA_INDEX_AVAILABLE or not self.index:
            return {
                "available": False,
                "document_count": 0,
                "error": "Index not available"
            }
        
        try:
            doc_store = self.index.storage_context.docstore
            return {
                "available": True,
                "document_count": len(doc_store.docs),
                "persist_dir": str(self.persist_dir),
                "index_type": "VectorStoreIndex"
            }
        except Exception as e:
            return {
                "available": False,
                "error": str(e)
            }
    
    def clear_index(self) -> bool:
        """Clear all documents from the index"""
        try:
            if self.persist_dir.exists():
                import shutil
                shutil.rmtree(self.persist_dir)
                self.persist_dir.mkdir(parents=True, exist_ok=True)
            
            self.index = None
            self.query_engine = None
            
            if LLAMA_INDEX_AVAILABLE:
                self._initialize_index()
            
            logger.info("Index cleared successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing index: {e}")
            return False


# Global llama-index service instance
llama_index_service = LlamaIndexService()


def get_llama_index_service() -> LlamaIndexService:
    """Get the global LlamaIndex service instance"""
    return llama_index_service