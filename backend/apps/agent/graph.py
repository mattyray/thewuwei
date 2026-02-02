"""
LangGraph agent for WuWei.

The graph orchestrates the conversation flow:
1. Receive user message
2. Call Claude with tool definitions
3. Execute any tool calls
4. Return response (with streaming support)
"""

from typing import Annotated, Any

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from typing_extensions import TypedDict

from . import tools as agent_tools
from .prompts import SYSTEM_PROMPT


# --- LangChain tool wrappers ---
# These wrap our pure business logic functions as LangChain tools
# so the LLM can call them. The user is injected from graph config.


@tool
def log_meditation(duration_minutes: int | None = None) -> dict:
    """Log that the user completed their meditation.

    Args:
        duration_minutes: Optional duration in minutes
    """
    # User is injected at runtime via config
    raise NotImplementedError("Must be called via graph with user config")


@tool
def save_gratitude_list(items: list[str]) -> dict:
    """Save the user's gratitude list for today.

    Args:
        items: List of things the user is grateful for
    """
    raise NotImplementedError


@tool
def save_journal_entry(content: str) -> dict:
    """Save a journal entry for today. This will trigger an AI reflection.

    Args:
        content: The journal entry content
    """
    raise NotImplementedError


@tool
def create_todo(task: str, due_date: str | None = None) -> dict:
    """Create a new todo item.

    Args:
        task: The task description
        due_date: Optional due date (YYYY-MM-DD format, or "today", "tomorrow")
    """
    raise NotImplementedError


@tool
def complete_todo(search: str) -> dict:
    """Mark a todo as complete by searching for it.

    Args:
        search: Text to search for in todo tasks
    """
    raise NotImplementedError


@tool
def get_todos(include_completed: bool = False) -> dict:
    """Get the user's todo list.

    Args:
        include_completed: Whether to include completed todos
    """
    raise NotImplementedError


@tool
def get_recent_entries(days: int = 7) -> dict:
    """Get recent journal entries.

    Args:
        days: Number of days to look back
    """
    raise NotImplementedError


@tool
def get_mantras() -> dict:
    """Get the user's mantras/reminders."""
    raise NotImplementedError


@tool
def add_mantra(content: str) -> dict:
    """Add a new mantra.

    Args:
        content: The mantra text
    """
    raise NotImplementedError


@tool
def get_todays_status() -> dict:
    """Get today's check-in status and overview."""
    raise NotImplementedError


TOOLS = [
    log_meditation,
    save_gratitude_list,
    save_journal_entry,
    create_todo,
    complete_todo,
    get_todos,
    get_recent_entries,
    get_mantras,
    add_mantra,
    get_todays_status,
]

# Map tool names to our business logic functions
TOOL_FUNCTIONS = {
    "log_meditation": agent_tools.log_meditation,
    "save_gratitude_list": agent_tools.save_gratitude_list,
    "save_journal_entry": agent_tools.save_journal_entry,
    "create_todo": agent_tools.create_todo,
    "complete_todo": agent_tools.complete_todo,
    "get_todos": agent_tools.get_todos,
    "get_recent_entries": agent_tools.get_recent_entries,
    "get_mantras": agent_tools.get_mantras,
    "add_mantra": agent_tools.add_mantra,
    "get_todays_status": agent_tools.get_todays_status,
}


# --- Graph state ---


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


# --- Graph nodes ---


def call_model(state: AgentState, config: RunnableConfig) -> dict:
    """Call Claude with the current conversation and tool definitions."""
    model_name = config.get("configurable", {}).get(
        "model", "claude-sonnet-4-20250514"
    )
    api_key = config.get("configurable", {}).get("anthropic_api_key")

    model = ChatAnthropic(
        model=model_name,
        anthropic_api_key=api_key,
        max_tokens=1024,
    )
    model_with_tools = model.bind_tools(TOOLS)

    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    response = model_with_tools.invoke(messages)

    return {"messages": [response]}


def execute_tools(state: AgentState, config: RunnableConfig) -> dict:
    """Execute tool calls from the model's response."""
    user = config.get("configurable", {}).get("user")
    last_message = state["messages"][-1]

    results = []
    for tool_call in last_message.tool_calls:
        func = TOOL_FUNCTIONS[tool_call["name"]]
        # Inject user into the tool call
        kwargs = tool_call["args"].copy()
        kwargs["user"] = user
        result = func(**kwargs)

        from langchain_core.messages import ToolMessage

        results.append(
            ToolMessage(
                content=str(result),
                tool_call_id=tool_call["id"],
                name=tool_call["name"],
            )
        )

    return {"messages": results}


def should_continue(state: AgentState) -> str:
    """Route based on whether the model wants to call tools."""
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return END


# --- Build the graph ---


def build_graph() -> StateGraph:
    """Build and compile the LangGraph agent."""
    graph = StateGraph(AgentState)

    graph.add_node("model", call_model)
    graph.add_node("tools", execute_tools)

    graph.set_entry_point("model")
    graph.add_conditional_edges("model", should_continue, {
        "tools": "tools",
        END: END,
    })
    graph.add_edge("tools", "model")

    return graph.compile()


# Singleton compiled graph
agent = build_graph()
