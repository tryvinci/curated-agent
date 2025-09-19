from crewai import Agent, Task, Crew
from crewai.tools import tool
from langchain_anthropic import ChatAnthropic
from typing import Dict, Any, Optional
import logging

from app.core.config import get_settings

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
    
    def create_creative_agents(self) -> Dict[str, Agent]:
        """Create specialized agents for creative workflow"""
        
        # Creative Director Agent
        creative_director = Agent(
            role="Creative Director",
            goal="Oversee and guide the creative process with strategic vision",
            backstory="You are an experienced creative director who understands "
                     "brand strategy, creative vision, and can guide teams to "
                     "produce exceptional creative work.",
            llm=self.llm,
            verbose=True
        )
        
        # Content Creator Agent
        content_creator = Agent(
            role="Content Creator",
            goal="Generate engaging and original creative content",
            backstory="You are a talented content creator with expertise in "
                     "writing, storytelling, and creating compelling narratives "
                     "across various formats and platforms.",
            llm=self.llm,
            verbose=True
        )
        
        # Quality Reviewer Agent
        quality_reviewer = Agent(
            role="Quality Reviewer",
            goal="Review and refine creative outputs for excellence",
            backstory="You are a meticulous quality reviewer who ensures "
                     "all creative work meets high standards of quality, "
                     "consistency, and effectiveness.",
            llm=self.llm,
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