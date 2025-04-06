import pytest
import asyncio
from datetime import datetime
from unittest.mock import MagicMock, patch, AsyncMock

from app.agents.assistant import AssistantAgent
from app.agents.types import AgentRole, AgentStatus
from camel.messages import BaseMessage

# Sample tool for testing
# Make the func async
async def sample_tool_func(**kwargs):
    return {"result": "test result"}

SAMPLE_TOOL = {
    "name": "test_tool",
    "description": "A test tool for testing purposes",
    "func": sample_tool_func
}

@pytest.fixture
def mock_llm_model():
    """Mock LLM model for testing"""
    return MagicMock()

@pytest.fixture
def mock_chat_agent():
    """Mock ChatAgent for testing"""
    mock = MagicMock()
    analysis_response = MagicMock(message='{"main_task": "Analyze Python info", "needs_tools": true, "subtasks": ["Search web"]}')
    plan_response = MagicMock(message='{"tools": [{"name": "test_tool", "args": {"query": "Python"}}]}')

    async def side_effect(*args, **kwargs):
        message_content = args[0].content if args else ""
        if "Analyze this user request" in message_content:
            return analysis_response
        elif "determine which tools to use" in message_content:
            return plan_response
        else:
             return MagicMock(message='{"response": "Okay, I can help with that."}')

    mock.record_message = AsyncMock(side_effect=side_effect)
    return mock

@pytest.fixture
def assistant(mock_llm_model, mock_chat_agent):
    """Create an assistant instance for testing"""
    with patch('app.services.llm.get_llm_model', return_value=mock_llm_model), \
         patch('app.agents.base.ChatAgent', return_value=mock_chat_agent):
        assistant = AssistantAgent(
            tools=[SAMPLE_TOOL],
            model_name="openai/gpt-4o-mini"
        )
        return assistant

@pytest.mark.asyncio
async def test_assistant_initialization(assistant):
    """Test that the assistant initializes correctly"""
    assert assistant.role == AgentRole.ASSISTANT
    assert assistant.status == AgentStatus.IDLE
    assert len(assistant.tools) == 1
    assert assistant.memory_size == 20
    assert isinstance(assistant.agent.record_message, AsyncMock)

@pytest.mark.asyncio
async def test_analyze_request(assistant):
    """Test request analysis"""
    message = "Can you help me search for information about Python?"
    analysis = await assistant._analyze_request(message)
    
    assert isinstance(analysis, dict)
    assert "main_task" in analysis
    assert analysis["main_task"] == "Analyze Python info"
    assert "needs_tools" in analysis
    assert analysis["needs_tools"] is True
    assert "subtasks" in analysis

@pytest.mark.asyncio
async def test_plan_tool_usage(assistant):
    """Test tool usage planning"""
    message = "Can you help me search for information about Python?"
    analysis = {
        "main_task": "Search for Python information",
        "needs_tools": True,
        "subtasks": ["Search web", "Format results"]
    }
    
    tools_plan = await assistant._plan_tool_usage(message, analysis)
    assert isinstance(tools_plan, list)
    assert len(tools_plan) > 0
    assert tools_plan[0]["name"] == "test_tool"
    assert tools_plan[0]["args"]["query"] == "Python"

@pytest.mark.asyncio
async def test_process_message(assistant):
    """Test the full message processing flow"""
    message = "Hello, can you help me?"
    status_updates = []
    
    async for update in assistant.process(message):
        status_updates.append(update)
        
        # Verify update structure
        assert "type" in update
        assert "timestamp" in update
        assert "agent_role" in update
        assert "status" in update
        assert isinstance(update["timestamp"], datetime)
        
    # Verify we got status updates
    assert len(status_updates) > 0
    
    # Verify final status
    final_update = status_updates[-1]
    assert final_update["status"] in [AgentStatus.DONE, AgentStatus.ERROR]
    assert len(assistant.chat_history) >= 2
    assert assistant.chat_history[-1]["role"] == "assistant"
    assert "Okay, I can help" in assistant.chat_history[-1]["content"]

@pytest.mark.asyncio
async def test_error_handling(assistant):
    """Test error handling during processing"""
    error_message = "Forced analysis error"
    assistant.agent.record_message.side_effect = Exception(error_message)

    async for update in assistant.process("This should fail"):
        if update["status"] == AgentStatus.ERROR:
            assert update["error"] is not None
            assert error_message in update["error"]
            break
    else:
        pytest.fail("No error status received") 