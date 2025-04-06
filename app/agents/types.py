from typing import Dict, List, Any, Optional, Union, AsyncGenerator, TypedDict
from enum import Enum
from datetime import datetime

class AgentRole(str, Enum):
    """Enum for different agent roles in the system"""
    ASSISTANT = "assistant"  # Main assistant agent that interacts with user
    PLANNER = "planner"     # Agent responsible for task planning
    EXECUTOR = "executor"   # Agent that executes specific tasks
    CRITIC = "critic"       # Agent that reviews and critiques actions

class AgentStatus(str, Enum):
    """Enum for agent execution status"""
    IDLE = "idle"           # Agent is not doing anything
    THINKING = "thinking"   # Agent is processing/thinking
    EXECUTING = "executing" # Agent is executing a task
    WAITING = "waiting"     # Agent is waiting for something
    ERROR = "error"         # Agent encountered an error
    DONE = "done"          # Agent completed its task

class AgentUpdate(TypedDict):
    """Type for agent status updates"""
    type: str              # Type of update (status, message, error, etc.)
    timestamp: datetime    # When this update occurred
    agent_role: AgentRole  # Which agent is sending this update
    status: AgentStatus   # Current status of the agent
    message: Optional[str] # Optional message with the update
    task: Optional[str]   # Current task being performed
    error: Optional[str]  # Error message if any

class AgentResult(TypedDict):
    """Type for final agent execution results"""
    success: bool         # Whether the execution was successful
    message: str         # Final response or error message
    chat_history: List[Dict[str, Any]]  # History of the conversation
    token_count: int     # Number of tokens used
    execution_time: float  # Time taken to execute
    error: Optional[str]  # Error message if any

# Tool-related types
class ToolMetadata(TypedDict):
    """Type for tool metadata"""
    name: str            # Name of the tool
    description: str     # Description of what the tool does
    parameters: Dict[str, Any]  # Parameters the tool accepts
    required: List[str]  # Required parameters
    returns: Dict[str, Any]  # Description of what the tool returns

class ToolResult(TypedDict):
    """Type for tool execution results"""
    success: bool        # Whether the tool execution was successful
    result: Any         # The result of the tool execution
    error: Optional[str]  # Error message if any 