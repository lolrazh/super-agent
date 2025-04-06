from typing import Dict, List, Any, Optional, AsyncGenerator, Callable
from datetime import datetime
import asyncio
import logging
from abc import ABC, abstractmethod

from camel.agents import ChatAgent
from camel.messages import BaseMessage, OpenAISystemMessage
from .types import AgentRole, AgentStatus, AgentUpdate, AgentResult, ToolResult

logger = logging.getLogger(__name__)

class ToolWrapper:
    """Wrapper class for tools to provide the interface expected by ChatAgent"""
    def __init__(self, name: str, description: str, func: Callable):
        self.name = name
        self.description = description
        self.func = func
    
    def get_function_name(self) -> str:
        """Get the name of the function"""
        return self.name

class BaseAgent(ABC):
    """Base class for all agents in the system"""
    
    def __init__(
        self,
        role: AgentRole,
        model_name: str,
        tools: Optional[List[Dict[str, Any]]] = None,
        memory_size: int = 10
    ):
        """
        Initialize the base agent
        
        Args:
            role: The role this agent plays in the system
            model_name: Name of the LLM model to use
            tools: Optional list of tools this agent has access to
            memory_size: Number of past interactions to remember
        """
        self.role = role
        self.model_name = model_name
        self.tools = tools or []
        self.memory_size = memory_size
        self.status = AgentStatus.IDLE
        self.chat_history: List[Dict[str, Any]] = []
        self.token_count = 0
        
        # Initialize the underlying CAMEL agent
        self._init_camel_agent()
    
    def _init_camel_agent(self):
        """Initialize the underlying CAMEL agent"""
        try:
            from app.services.llm import get_llm_model
            
            # Get the LLM model
            model = get_llm_model(self.model_name)
            
            # Convert tools to wrapped instances
            camel_tools = []
            for tool in self.tools:
                camel_tool = ToolWrapper(
                    name=tool["name"],
                    description=tool["description"],
                    func=tool["func"]
                )
                camel_tools.append(camel_tool)
            
            # Create the CAMEL agent with our role
            system_message = BaseMessage(role_name='assistant', role_type='system', meta_dict={}, content=self._get_system_message())
            self.agent = ChatAgent(
                model=model,
                system_message=system_message,
                tools=camel_tools
            )
        except Exception as e:
            logger.error(f"Failed to initialize CAMEL agent: {str(e)}")
            self.agent = None
            raise
    
    @abstractmethod
    def _get_system_message(self) -> str:
        """
        Get the system message that defines this agent's role and behavior
        
        This should be implemented by each specific agent type
        """
        pass
    
    async def _update_status(self, status: AgentStatus, task: Optional[str] = None) -> AgentUpdate:
        """
        Update the agent's status and create an update message
        
        Args:
            status: New status
            task: Optional description of current task
            
        Returns:
            Update message to be sent to clients
        """
        self.status = status
        
        update: AgentUpdate = {
            "type": "agent_status",
            "timestamp": datetime.now(),
            "agent_role": self.role,
            "status": status,
            "message": None,
            "task": task,
            "error": None
        }
        
        return update
    
    async def _execute_tool(self, tool_name: str, **kwargs) -> ToolResult:
        """
        Execute a tool and handle any errors
        
        Args:
            tool_name: Name of the tool to execute
            **kwargs: Arguments to pass to the tool
            
        Returns:
            Result of the tool execution
        """
        try:
            # Find the tool
            tool = next((t for t in self.tools if t["name"] == tool_name), None)
            if not tool:
                raise ValueError(f"Tool {tool_name} not found")
            
            # Execute the tool
            result = await tool["func"](**kwargs)
            
            return {
                "success": True,
                "result": result,
                "error": None
            }
        except Exception as e:
            logger.error(f"Tool execution failed: {str(e)}")
            return {
                "success": False,
                "result": None,
                "error": str(e)
            }
    
    @abstractmethod
    async def process(self, message: str) -> AsyncGenerator[AgentUpdate, None]:
        """
        Process a message and generate updates
        
        This should be implemented by each specific agent type
        
        Args:
            message: The message to process
            
        Yields:
            Updates about the agent's progress
        """
        pass
    
    def get_result(self) -> AgentResult:
        """
        Get the final result of the agent's execution
        
        Returns:
            Final result including success status, message, and history
        """
        return {
            "success": self.status == AgentStatus.DONE,
            "message": self.chat_history[-1]["content"] if self.chat_history else "",
            "chat_history": self.chat_history,
            "token_count": self.token_count,
            "execution_time": 0.0,  # This should be tracked by specific implementations
            "error": None if self.status != AgentStatus.ERROR else "Execution failed"
        } 