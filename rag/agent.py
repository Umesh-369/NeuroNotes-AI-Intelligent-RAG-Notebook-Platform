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
    extract_images_from_document,
    remove_pages_from_document
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
    extract_images_from_document,
    remove_pages_from_document
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
        f"You are a highly capable AI assistant operating within 'Notebook {state['notebook_id']}'.\n"
        "Your primary job is to help the user understand, extract, edit, and generate content based on the documents in this notebook.\n\n"
        
        "CAPABILITIES & WORKFLOW:\n"
        "1. If a user asks a general question about their documents, use `search_knowledge_base` first.\n"
        "2. If a user asks to summarize, extract key points, or rewrite an entire document, use `read_full_document` first to get the content, and then use `create_derived_document` to save the results as a new file in the notebook.\n"
        "3. If a user asks to extract images or copy images into a new document, use `extract_images_from_document`.\n"
        "4. If a user asks to remove specific pages (like 'remove the last page' or 'delete page 3'), use `remove_pages_from_document`.\n"
        "   - IMPORTANT: `remove_pages_from_document` has an `overwrite` argument. If the user asks to 'modify the existing pdf' or 'update this document', set `overwrite=True`.\n"
        "   - If they ask to 'save as a new document' or 'put in a new document', set `overwrite=False`.\n"
        "5. You must actively use your tools if the user implies they want an action performed.\n\n"
        
        "IMPORTANT FORMATTING RULES:\n"
        "- The frontend chat UI does NOT render Markdown. \n"
        "- DO NOT use any markdown characters like **, *, #, -, or ` in your final response to the user.\n"
        "- Use plain text, clear paragraphs, and standard punctuation only.\n"
        "- If you successfully created a document, tell the user the specific name of it."
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
