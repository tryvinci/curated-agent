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
    from llama_index.core.tools import FunctionTool
    from llama_index.readers.file import PDFReader, DocxReader
    LLAMA_INDEX_AVAILABLE = True
except ImportError:
    logger = logging.getLogger(__name__)
    logger.warning("LlamaIndex not available - document processing features will be limited")
    LLAMA_INDEX_AVAILABLE = False

from app.core.config import get_settings

# Import external MCP client
try:
    from app.services.external_mcp_client import get_external_mcp_client, ExternalMCPServerResult
    EXTERNAL_MCP_AVAILABLE = True
except ImportError:
    EXTERNAL_MCP_AVAILABLE = False

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
        self.mcp_tools = []
        self.external_mcp_client = None
        self._initialize_index()
        self._setup_mcp_tools()
    
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
    
    def _setup_mcp_tools(self):
        """Set up MCP tools for use with LlamaIndex agents"""
        if not LLAMA_INDEX_AVAILABLE or not EXTERNAL_MCP_AVAILABLE:
            return
        
        async def get_client():
            if self.external_mcp_client is None:
                self.external_mcp_client = await get_external_mcp_client()
            return self.external_mcp_client
        
        def generate_image_sync(prompt: str, style: str = None, size: str = "1024x1024") -> str:
            """Generate an image using external MCP server"""
            import asyncio
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            try:
                client = loop.run_until_complete(get_client())
                result = loop.run_until_complete(
                    client.generate_image(prompt, style, size)
                )
                if result.success:
                    return f"Image generated successfully: {result.result}"
                else:
                    return f"Image generation failed: {result.error}"
            except Exception as e:
                return f"Error generating image: {str(e)}"
        
        def generate_tts_sync(text: str, voice: str = None, format: str = "mp3") -> str:
            """Generate text-to-speech using external MCP server"""
            import asyncio
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            try:
                client = loop.run_until_complete(get_client())
                result = loop.run_until_complete(
                    client.generate_tts(text, voice, format)
                )
                if result.success:
                    return f"TTS generated successfully: {result.result}"
                else:
                    return f"TTS generation failed: {result.error}"
            except Exception as e:
                return f"Error generating TTS: {str(e)}"
        
        def generate_video_sync(prompt: str, duration: int = 30, style: str = None) -> str:
            """Generate a video using external MCP server"""
            import asyncio
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            try:
                client = loop.run_until_complete(get_client())
                result = loop.run_until_complete(
                    client.generate_video(prompt, duration, style)
                )
                if result.success:
                    return f"Video generated successfully: {result.result}"
                else:
                    return f"Video generation failed: {result.error}"
            except Exception as e:
                return f"Error generating video: {str(e)}"
        
        def call_external_mcp_tool_sync(server_name: str, tool_name: str, **kwargs) -> str:
            """Call any tool on external MCP server"""
            import asyncio
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            try:
                client = loop.run_until_complete(get_client())
                result = loop.run_until_complete(
                    client.call_external_tool(server_name, tool_name, kwargs)
                )
                if result.success:
                    return f"Tool {tool_name} executed successfully: {result.result}"
                else:
                    return f"Tool {tool_name} failed: {result.error}"
            except Exception as e:
                return f"Error calling external tool: {str(e)}"
        
        # Create LlamaIndex FunctionTools from MCP capabilities
        try:
            self.mcp_tools = [
                FunctionTool.from_defaults(
                    fn=generate_image_sync,
                    name="generate_image",
                    description="Generate images using external MCP server. Parameters: prompt (required), style (optional), size (optional, default '1024x1024')"
                ),
                FunctionTool.from_defaults(
                    fn=generate_tts_sync,
                    name="generate_tts",
                    description="Generate text-to-speech using external MCP server. Parameters: text (required), voice (optional), format (optional, default 'mp3')"
                ),
                FunctionTool.from_defaults(
                    fn=generate_video_sync,
                    name="generate_video",
                    description="Generate videos using external MCP server. Parameters: prompt (required), duration (optional, default 30), style (optional)"
                ),
                FunctionTool.from_defaults(
                    fn=call_external_mcp_tool_sync,
                    name="call_external_mcp_tool",
                    description="Call any tool on external MCP server. Parameters: server_name (required), tool_name (required), plus any tool-specific parameters"
                )
            ]
            logger.info(f"Set up {len(self.mcp_tools)} MCP tools for LlamaIndex")
        except Exception as e:
            logger.error(f"Failed to setup MCP tools: {e}")
            self.mcp_tools = []
    
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
    
    def get_mcp_tools(self) -> List[Any]:
        """Get available MCP tools for use with LlamaIndex agents"""
        return self.mcp_tools if hasattr(self, 'mcp_tools') else []
    
    def create_agent_with_tools(self, system_message: str = None):
        """Create a LlamaIndex agent with MCP tools"""
        if not LLAMA_INDEX_AVAILABLE:
            logger.error("LlamaIndex not available")
            return None
        
        try:
            from llama_index.core.agent import ReActAgent
            from llama_index.llms.anthropic import Anthropic
            
            # Use Anthropic Claude as the LLM
            llm = Anthropic(
                api_key=settings.anthropic_api_key,
                model="claude-3-sonnet-20240229"
            )
            
            # Combine document search with MCP tools
            all_tools = []
            
            # Add query engine as a tool if we have an index
            if self.query_engine:
                def search_documents_sync(query: str) -> str:
                    """Search through the document knowledge base"""
                    try:
                        response = self.query_engine.query(query)
                        return str(response)
                    except Exception as e:
                        return f"Search error: {str(e)}"
                
                from llama_index.core.tools import FunctionTool
                search_tool = FunctionTool.from_defaults(
                    fn=search_documents_sync,
                    name="search_documents",
                    description="Search through uploaded documents and knowledge base"
                )
                all_tools.append(search_tool)
            
            # Add MCP tools
            all_tools.extend(self.mcp_tools)
            
            if not all_tools:
                logger.warning("No tools available for agent")
                return None
            
            # Create the agent
            agent = ReActAgent.from_tools(
                tools=all_tools,
                llm=llm,
                system_prompt=system_message or "You are a helpful assistant with access to document search and external tools for image, TTS, and video generation.",
                verbose=True
            )
            
            logger.info(f"Created LlamaIndex agent with {len(all_tools)} tools")
            return agent
            
        except Exception as e:
            logger.error(f"Failed to create agent with tools: {e}")
            return None
    
    async def query_with_tools(self, query: str, system_message: str = None) -> Dict[str, Any]:
        """Query using LlamaIndex agent with MCP tools"""
        try:
            agent = self.create_agent_with_tools(system_message)
            if not agent:
                return {
                    "success": False,
                    "error": "Could not create agent"
                }
            
            response = agent.chat(query)
            
            return {
                "success": True,
                "query": query,
                "response": str(response),
                "tools_used": getattr(response, 'tool_calls', []) if hasattr(response, 'tool_calls') else []
            }
            
        except Exception as e:
            logger.error(f"Error querying with tools: {e}")
            return {
                "success": False,
                "error": str(e)
            }


# Global llama-index service instance
llama_index_service = LlamaIndexService()


def get_llama_index_service() -> LlamaIndexService:
    """Get the global LlamaIndex service instance"""
    return llama_index_service