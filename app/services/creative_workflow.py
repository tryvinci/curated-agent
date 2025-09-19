from crewai import Agent, Task, Crew
from crewai.tools import tool
from langchain_anthropic import ChatAnthropic
from typing import Dict, Any, Optional
import logging

from app.core.config import get_settings

# Import new services with graceful handling
try:
    from app.services.mcp_integration import get_mcp_integration
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False

try:
    from app.services.llama_index_service import get_llama_index_service
    LLAMA_INDEX_AVAILABLE = True
except ImportError:
    LLAMA_INDEX_AVAILABLE = False

try:
    from app.services.external_mcp_client import get_external_mcp_client
    EXTERNAL_MCP_AVAILABLE = True
except ImportError:
    EXTERNAL_MCP_AVAILABLE = False

settings = get_settings()
logger = logging.getLogger(__name__)


class CreativeWorkflowService:
    """Service for managing CrewAI-based creative workflows"""
    
    def __init__(self):
        if not settings.anthropic_api_key:
            raise ValueError("Anthropic API key is required for CrewAI integration")
            
        # Initialize Anthropic Claude LLM
        self.llm = ChatAnthropic(
            model="claude-3-sonnet-20240229",
            anthropic_api_key=settings.anthropic_api_key,
            temperature=0.7
        )
        
        # Initialize MCP and LlamaIndex services if available
        self.mcp_service = get_mcp_integration() if MCP_AVAILABLE else None
        self.llama_index_service = get_llama_index_service() if LLAMA_INDEX_AVAILABLE else None
        self.external_mcp_client = None
        
        # Set up enhanced tools
        self._setup_enhanced_tools()
    
    def _setup_enhanced_tools(self):
        """Set up enhanced tools using MCP and LlamaIndex"""
        
        @tool("search_knowledge_base")
        def search_knowledge_base(query: str) -> str:
            """Search the document knowledge base for relevant information"""
            if not self.llama_index_service:
                return "Document search not available - LlamaIndex not installed"
            
            try:
                result = self.llama_index_service.search_documents(query, top_k=3)
                if result.success and result.results:
                    search_results = []
                    for r in result.results:
                        search_results.append(f"• {r.get('text', 'No text')[:200]}...")
                    return f"Knowledge base search results for '{query}':\n" + "\n".join(search_results)
                else:
                    return f"No relevant information found for: {query}"
            except Exception as e:
                return f"Search error: {str(e)}"
        
        @tool("execute_mcp_tool")
        def execute_mcp_tool(tool_name: str, **kwargs) -> str:
            """Execute an MCP tool with given parameters"""
            if not self.mcp_service:
                return "MCP tools not available - MCP not installed"
            
            try:
                # This would be async in real implementation, but for simplicity...
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(
                    self.mcp_service.execute_tool(tool_name, **kwargs)
                )
                loop.close()
                
                if result.success:
                    return f"Tool '{tool_name}' executed successfully: {result.result}"
                else:
                    return f"Tool '{tool_name}' failed: {result.error}"
            except Exception as e:
                return f"MCP tool execution error: {str(e)}"
        
        @tool("generate_image")
        def generate_image(prompt: str, style: str = None) -> str:
            """Generate an image using external MCP server"""
            if not EXTERNAL_MCP_AVAILABLE:
                return "External MCP services not available"
            
            try:
                import asyncio
                if self.external_mcp_client is None:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    self.external_mcp_client = loop.run_until_complete(get_external_mcp_client())
                
                loop = asyncio.get_event_loop()
                result = loop.run_until_complete(
                    self.external_mcp_client.generate_image(prompt, style)
                )
                
                if result.success:
                    return f"Image generated successfully: {result.result}"
                else:
                    return f"Image generation failed: {result.error}"
            except Exception as e:
                return f"Error generating image: {str(e)}"
        
        @tool("generate_tts")
        def generate_tts(text: str, voice: str = None) -> str:
            """Generate text-to-speech using external MCP server"""
            if not EXTERNAL_MCP_AVAILABLE:
                return "External MCP services not available"
            
            try:
                import asyncio
                if self.external_mcp_client is None:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    self.external_mcp_client = loop.run_until_complete(get_external_mcp_client())
                
                loop = asyncio.get_event_loop()
                result = loop.run_until_complete(
                    self.external_mcp_client.generate_tts(text, voice)
                )
                
                if result.success:
                    return f"TTS generated successfully: {result.result}"
                else:
                    return f"TTS generation failed: {result.error}"
            except Exception as e:
                return f"Error generating TTS: {str(e)}"
        
        @tool("generate_video") 
        def generate_video(prompt: str, duration: int = 30, style: str = None) -> str:
            """Generate a video using external MCP server"""
            if not EXTERNAL_MCP_AVAILABLE:
                return "External MCP services not available"
            
            try:
                import asyncio
                if self.external_mcp_client is None:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    self.external_mcp_client = loop.run_until_complete(get_external_mcp_client())
                
                loop = asyncio.get_event_loop()
                result = loop.run_until_complete(
                    self.external_mcp_client.generate_video(prompt, duration, style)
                )
                
                if result.success:
                    return f"Video generated successfully: {result.result}"
                else:
                    return f"Video generation failed: {result.error}"
            except Exception as e:
                return f"Error generating video: {str(e)}"
        
        # Store tools for use by agents
        self.enhanced_tools = [
            search_knowledge_base, 
            execute_mcp_tool, 
            generate_image,
            generate_tts,
            generate_video
        ]
        
    def create_creative_agents(self) -> Dict[str, Agent]:
        """Create specialized agents for creative workflow with enhanced tools"""
        """Create specialized agents for creative workflow with enhanced tools"""
        
        # Creative Director Agent with enhanced capabilities
        creative_director = Agent(
            role="Creative Director",
            goal="Oversee and guide the creative process with strategic vision, leveraging available tools and knowledge",
            backstory="You are an experienced creative director who understands "
                     "brand strategy, creative vision, and can guide teams to "
                     "produce exceptional creative work. You have access to tools "
                     "for research and content generation.",
            llm=self.llm,
            tools=self.enhanced_tools if hasattr(self, 'enhanced_tools') else [],
            verbose=True
        )
        
        # Content Creator Agent with tool access
        content_creator = Agent(
            role="Content Creator",
            goal="Generate engaging and original creative content using available research and tools",
            backstory="You are a talented content creator with expertise in "
                     "writing, storytelling, and creating compelling narratives "
                     "across various formats and platforms. You can search knowledge "
                     "bases and use specialized tools to enhance your content.",
            llm=self.llm,
            tools=self.enhanced_tools if hasattr(self, 'enhanced_tools') else [],
            verbose=True
        )
        
        # Quality Reviewer Agent
        quality_reviewer = Agent(
            role="Quality Reviewer",
            goal="Review and refine creative outputs for excellence, ensuring accuracy with fact-checking",
            backstory="You are a meticulous quality reviewer who ensures "
                     "all creative work meets high standards of quality, "
                     "consistency, and effectiveness. You can verify information "
                     "using available knowledge sources.",
            llm=self.llm,
            tools=self.enhanced_tools if hasattr(self, 'enhanced_tools') else [],
            verbose=True
        )
        
        return {
            "creative_director": creative_director,
            "content_creator": content_creator,
            "quality_reviewer": quality_reviewer
        }
    
    def create_creative_tasks(
        self, 
        agents: Dict[str, Agent], 
        task_description: str,
        project_context: Optional[str] = None,
        requirements: Optional[Dict[str, Any]] = None
    ) -> list[Task]:
        """Create tasks for the creative workflow"""
        
        context_info = f"Project Context: {project_context}\n" if project_context else ""
        requirements_info = f"Requirements: {requirements}\n" if requirements else ""
        
        # Strategy Task
        strategy_task = Task(
            description=f"""
            Develop a creative strategy for the following task:
            {task_description}
            
            {context_info}
            {requirements_info}
            
            Create a comprehensive creative brief including:
            1. Creative objectives
            2. Target audience analysis
            3. Key messaging and tone
            4. Creative direction and approach
            5. Success metrics
            
            Use the search_knowledge_base tool to research relevant information
            and get_available_tools to see what other capabilities are available.
            """,
            agent=agents["creative_director"],
            expected_output="A detailed creative brief and strategy document"
        )
        
        # Content Creation Task
        content_task = Task(
            description=f"""
            Based on the creative strategy, create the actual creative content for:
            {task_description}
            
            {context_info}
            {requirements_info}
            
            Ensure the content:
            1. Follows the creative brief
            2. Is engaging and original
            3. Meets all specified requirements
            4. Is appropriate for the target audience
            
            Use search_knowledge_base to find relevant background information
            and execute_mcp_tool if needed for content generation assistance.
            """,
            agent=agents["content_creator"],
            expected_output="High-quality creative content ready for review"
        )
        
        # Quality Review Task
        review_task = Task(
            description=f"""
            Review and refine the creative content created for:
            {task_description}
            
            Evaluate:
            1. Content quality and effectiveness
            2. Alignment with creative brief
            3. Grammar, style, and consistency
            4. Overall impact and engagement potential
            5. Factual accuracy (use search_knowledge_base to verify claims)
            
            Provide final polished version with improvement suggestions.
            """,
            agent=agents["quality_reviewer"],
            expected_output="Final reviewed and refined creative content with quality assessment"
        )
        
        return [strategy_task, content_task, review_task]
    
    def execute_workflow(
        self,
        task_description: str,
        project_context: Optional[str] = None,
        requirements: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute the complete creative workflow"""
        
        try:
            logger.info(f"Starting creative workflow for task: {task_description}")
            
            # Create agents and tasks
            agents = self.create_creative_agents()
            tasks = self.create_creative_tasks(
                agents, task_description, project_context, requirements
            )
            
            # Create and execute crew
            crew = Crew(
                agents=list(agents.values()),
                tasks=tasks,
                verbose=True
            )
            
            result = crew.kickoff()
            
            logger.info("Creative workflow completed successfully")
            
            return {
                "success": True,
                "result": str(result),
                "task_count": len(tasks),
                "agent_count": len(agents)
            }
            
        except Exception as e:
            logger.error(f"Error executing creative workflow: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "result": None
            }