from typing import AsyncGenerator, Dict, Any, Optional
import time
from datetime import datetime
import logging

from .base import BaseAgent
from .types import AgentRole, AgentStatus, AgentUpdate
from app.config import settings
from camel.messages import BaseMessage
from camel.types import OpenAIBackendRole

logger = logging.getLogger(__name__)

class AssistantAgent(BaseAgent):
    """Main assistant agent that interacts with users"""
    
    def __init__(self, tools=None, model_name=None):
        """Initialize the assistant agent"""
        super().__init__(
            role=AgentRole.ASSISTANT,
            model_name=model_name or settings.ASSISTANT_MODEL,
            tools=tools,
            memory_size=20  # Assistant keeps more context
        )
        self.start_time = None
    
    def _get_system_message(self) -> str:
        """Get the system message that defines the assistant's role"""
        return """You are a highly capable AI assistant with access to various tools.
Your role is to:
1. Understand user requests thoroughly
2. Break down complex tasks into manageable steps
3. Use available tools appropriately to accomplish tasks
4. Provide clear, helpful responses
5. Maintain context and coherence throughout conversations
6. Be proactive in asking for clarification when needed
7. Always verify your actions and results

Remember to:
- Think step-by-step
- Explain your reasoning when appropriate
- Be concise but informative
- Handle errors gracefully
- Stay within the scope of available tools
- Respect user preferences and constraints"""

    async def process(self, message: str) -> AsyncGenerator[AgentUpdate, None]:
        """
        Process a user message and generate responses
        
        Args:
            message: The user's message
            
        Yields:
            Updates about the assistant's progress
        """
        try:
            self.start_time = time.time()
            
            # Update status to thinking
            yield await self._update_status(
                status=AgentStatus.THINKING,
                task="Understanding your request"
            )
            
            # First, analyze the message to understand the request
            analysis = await self._analyze_request(message)
            
            # If tools are needed, identify which ones
            if analysis.get("needs_tools", False):
                yield await self._update_status(
                    status=AgentStatus.THINKING,
                    task="Planning tool usage"
                )
                tools_to_use = await self._plan_tool_usage(message, analysis)
                
                # Execute tools if needed
                if tools_to_use:
                    yield await self._update_status(
                        status=AgentStatus.EXECUTING,
                        task=f"Using tools: {', '.join(t['name'] for t in tools_to_use)}"
                    )
                    tool_results = []
                    for tool in tools_to_use:
                        result = await self._execute_tool(
                            tool["name"],
                            **tool.get("args", {})
                        )
                        tool_results.append(result)
                        
                        # Update status for each tool execution
                        yield await self._update_status(
                            status=AgentStatus.EXECUTING,
                            task=f"Executed {tool['name']}"
                        )
            
            # Generate the response
            yield await self._update_status(
                status=AgentStatus.THINKING,
                task="Generating response"
            )
            
            # Use the CAMEL agent to generate the response
            response = await self.agent.record_message(
                BaseMessage(
                    content=message,
                    role_name="user",
                    role_type="user",
                    meta_dict={}
                )
            )
            
            # Add to chat history
            self.chat_history.append({
                "role": "user",
                "content": message,
                "timestamp": datetime.now().isoformat()
            })
            self.chat_history.append({
                "role": "assistant",
                "content": response.message,
                "timestamp": datetime.now().isoformat()
            })
            
            # Update token count
            self.token_count += response.token_count
            
            # Final status update
            yield await self._update_status(
                status=AgentStatus.DONE,
                task=None
            )
            
        except Exception as e:
            # Handle any errors
            error_msg = f"Error processing message: {str(e)}"
            logger.error(error_msg)
            
            yield await self._update_status(
                status=AgentStatus.ERROR,
                task=None,
                error=error_msg
            )
            
    async def _analyze_request(self, message: str) -> Dict[str, Any]:
        """
        Analyze a user request to understand its requirements
        
        Args:
            message: The user's message
            
        Returns:
            Analysis results including whether tools are needed
        """
        if not self.agent:
            return {
                "main_task": message,
                "needs_tools": False,
                "subtasks": [],
                "constraints": [],
                "needs_clarification": False
            }

        # Use the CAMEL agent to analyze the request
        analysis_prompt = f"""Analyze this user request and provide structured information about:
1. The main task or question
2. Whether any tools might be needed
3. Any potential subtasks
4. Any constraints or preferences mentioned
5. Any missing information that needs clarification

User request: {message}

Provide your analysis in JSON format."""

        response = await self.agent.record_message(
            BaseMessage(
                content=analysis_prompt,
                role_name="user",
                role_type="user",
                meta_dict={}
            )
        )
        
        try:
            import json
            return json.loads(response.message)
        except:
            # If JSON parsing fails, return a basic analysis
            return {
                "main_task": message,
                "needs_tools": False,
                "subtasks": [],
                "constraints": [],
                "needs_clarification": False
            }
    
    async def _plan_tool_usage(self, message: str, analysis: Dict[str, Any]) -> list:
        """
        Plan which tools to use for a request
        
        Args:
            message: The user's message
            analysis: Analysis of the request
            
        Returns:
            List of tools to use with their arguments
        """
        if not self.tools or not self.agent:
            return []
            
        # Create a tool planning prompt
        tools_desc = "\n".join(f"- {t['name']}: {t['description']}" for t in self.tools)
        plan_prompt = f"""Based on this user request and analysis, determine which tools to use.

User request: {message}

Available tools:
{tools_desc}

Analysis:
{analysis}

Provide your tool usage plan in JSON format, including:
1. List of tools to use in sequence
2. Arguments for each tool
3. Reason for using each tool"""

        response = await self.agent.record_message(
            BaseMessage(
                content=plan_prompt,
                role_name="user",
                role_type="user",
                meta_dict={}
            )
        )
        
        try:
            import json
            plan = json.loads(response.message)
            return plan.get("tools", [])
        except:
            # If JSON parsing fails, return no tools
            return []

    async def _update_status(
        self,
        status: AgentStatus,
        task: Optional[str] = None,
        error: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update the agent's status

        Args:
            status: The new status
            task: Description of current task
            error: Error message if any

        Returns:
            Status update dict
        """
        elapsed = time.time() - self.start_time
        update = {
            "type": "agent_status",
            "timestamp": datetime.now(),
            "agent_role": self.role,
            "status": status,
            "task": task,
            "elapsed": elapsed,
            "error": error
        }
        return update 