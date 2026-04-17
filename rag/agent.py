import os
from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from rag.tools import (
    search_knowledge_base,
    read_full_document,
    list_notebook_documents,
    create_derived_document,
    remove_pages_from_document,
    web_search,
    fetch_url,
    send_email
)
from rag.document_processor import configure_gemini

# 1. Define the state for the agent graph
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    notebook_id: int

# 2. Define tools and LLM
tools = [
    list_notebook_documents,
    search_knowledge_base,
    read_full_document,
    create_derived_document,
    remove_pages_from_document,
    web_search,
    fetch_url,
    send_email
]

tool_node = ToolNode(tools)

# 3. Define the main agent node
def run_agent(state: AgentState):
    configure_gemini()
    
    if not os.environ.get("GOOGLE_API_KEY"):
        from langchain_core.messages import AIMessage
        return {"messages": [AIMessage(content="GOOGLE_API_KEY is not set. Please configure it to use the agent.")]}
        
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
    llm_with_tools = llm.bind_tools(tools)
    
    # Construct System Context
    system_instruction = (
        f"You are an advanced research assistant AI operating within 'Notebook {state['notebook_id']}'.\n"
        "Your primary job is to help the user with advanced research, document analysis, and comprehensive report generation.\n\n"
        
        "RESEARCH CAPABILITIES & WORKFLOW:\n"
        "1. When given a user topic, break it down into 3-5 focused sub-questions.\n"
        "2. Use `web_search` to find relevant information for these sub-questions.\n"
        "3. Use `fetch_url` to extract detailed textual content from the most important and relevant links.\n"
        "4. Gather multiple reliable sources. Avoid duplicate or low-quality sources, prefer recent and credible information, and stop searching when you have sufficient coverage.\n"
        "5. Generate a comprehensive report with the following structure:\n"
        "   - Title\n"
        "   - Executive Summary (5-6 lines)\n"
        "   - Key Findings (organized by themes)\n"
        "   - Important Insights\n"
        "   - Sources (with URLs)\n"
        "6. After generating the report, use the `send_email` tool to dispatch it to: s.u.s.hanumaprasad@gmail.com with the subject 'Research Report: <topic>'.\n\n"
        
        "NOTEBOOK OPERATIONS:\n"
        "You also retain your local notebook abilities. If the user asks about local documents:\n"
        "- Use `search_knowledge_base`, `read_full_document`, `create_derived_document`, or `remove_pages_from_document` as needed.\n\n"
        
        "IMPORTANT RULES:\n"
        "- Be efficient. Do not overuse tools (e.g., limit your recursive web searching to necessary bounds).\n"
        "- Ensure the final generated report is presented to the user. \n"
        "- The frontend chat UI does NOT render Markdown. \n"
        "- CRITICAL: DO NOT use any markdown characters like **, *, #, -, _, or ` in your final response to the user. Your output must be PLAIN TEXT ONLY. Use ALL CAPS for headers instead of bold or hashes. Use standard indentation and numbering for lists instead of asterisks or dashes."
    )
    
    system_message = SystemMessage(content=system_instruction)
    
    # Combine system prompt with the message history
    messages = [system_message] + state["messages"]
    
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

# 4. Build the LangGraph workflow
workflow = StateGraph(AgentState)
workflow.add_node("agent", run_agent)
workflow.add_node("tools", tool_node)

workflow.add_edge(START, "agent")

# Use prebuilt tools_condition: if agent returns a tool_call, route to tools; otherwise END.
workflow.add_conditional_edges("agent", tools_condition)
workflow.add_edge("tools", "agent")

# Compile the agent application with in-memory checkpointing for conversation history
memory = MemorySaver()
agent_app = workflow.compile(checkpointer=memory)
