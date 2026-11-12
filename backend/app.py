
import sys
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from langchain_ollama import ChatOllama
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent


# Project root directory
BASE_DIR = Path(__file__).resolve().parents[1]


# System instructions for AI assistant
SYSTEM_PROMPT = """
You are ExpenseAI, an intelligent expense management assistant.

You can help users with:
1. Adding expenses.
2. Viewing all expenses.
3. Deleting expenses.
4. Performing mathematical calculations.

You have access to MCP tools from two servers:
- Expense Management Server
- Math Calculation Server

Instructions:

- Always use the appropriate MCP tool when the user requests an action.
- Never claim an expense was added or deleted unless the corresponding tool succeeds.
- For viewing expenses, retrieve the actual database records.
- For calculations, use the mathematical tools instead of guessing.
- If required information is missing, ask the user for it.
- For adding expenses, collect amount, category, description and date.
- Never invent expense records or calculation results.
- Explain tool results in simple, friendly language.
- Display currency amounts in Indian Rupees (₹).
- Keep responses clear and concise.
"""


# Application lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):

    print("Connecting to MCP servers...")

    # Configure MCP servers
    client = MultiServerMCPClient({

        "expense": {
            "transport": "stdio",
            "command": sys.executable,
            "args": [
                str(
                    BASE_DIR
                    / "servers"
                    / "expense_server"
                    / "server.py"
                )
            ],
        },

        "calculation": {
            "transport": "stdio",
            "command": sys.executable,
            "args": [
                str(
                    BASE_DIR
                    / "servers"
                    / "calculation_server"
                    / "server.py"
                )
            ],
        },

    })

    # Discover tools from both MCP servers
    tools = await client.get_tools()

    print(f"Successfully loaded {len(tools)} MCP tools.")

    # Initialize Ollama model
    model = ChatOllama(model="qwen2.5:3b", temperature=0)

    # Create LangGraph ReAct agent
    agent = create_react_agent(
        model,
        tools,
        prompt=SYSTEM_PROMPT
    )

    app.state.agent = agent

    print("Ollama AI agent initialized successfully!")

    yield

    print("Shutting down AI Expense Tracker...")


# Initialize FastAPI application
app = FastAPI(
    title="AI Expense Tracker",
    description="AI chatbot powered by Ollama, LangGraph and MCP",
    version="1.0.0",
    lifespan=lifespan
)


# CORS configuration for HTML frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Chat request model
class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)


# Home endpoint
@app.get("/")
async def home():

    return {
        "message": "AI Expense Tracker API is running!",
        "model": "Ollama - Llama 3.1",
        "mcp_tools": 7
    }


# Chat endpoint
@app.post("/chat")
async def chat(request: ChatRequest):

    try:

        # Send user message to LangGraph agent
        response = await app.state.agent.ainvoke({
            "messages": [
                ("user", request.message)
            ]
        })

        # Extract final AI response
        answer = response["messages"][-1].content

        # Handle structured response content
        if isinstance(answer, list):

            answer = " ".join(
                item.get("text", "")
                for item in answer
                if isinstance(item, dict)
            )

        return {
            "reply": answer
        }

    except Exception as e:

        print(f"Chat error: {e}")

        raise HTTPException(
            status_code=500,
            detail="Something went wrong while processing your message."
        )
