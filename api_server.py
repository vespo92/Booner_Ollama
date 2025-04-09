"""
API server for Booner_Ollama that communicates with the MCP server.
This implements the server mode for the Booner_Ollama application.
"""

import os
import sys
import json
import asyncio
import logging
import uuid
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks, Request, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import httpx
import uvicorn

# Import Booner_Ollama components
from models.ollama_interface import OllamaInterface
from agents.infra_agent import InfrastructureAgent, OPNSenseAction
from agents.game_server_agent import GameServerAgent
from utils.config import Config
from utils.vector_store import VectorStore

# Setup logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Active task storage
active_tasks = {}

# Pydantic models for API requests and responses
class LLMGenerateRequest(BaseModel):
    model: str = Config.OLLAMA_LLM_MODEL
    prompt: str
    system: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 2048
    stream: bool = False

class LLMEmbedRequest(BaseModel):
    model: str = Config.OLLAMA_EMBED_MODEL
    text: str

class GameServerDeployRequest(BaseModel):
    game_type: str = Field(description="Type of game server (minecraft, cs2, valheim)")
    server_name: str = Field(description="Name of the server")
    port: int = Field(description="Port to run the server on")
    memory: str = Field(description="Memory allocation (e.g., '4G')")
    cpu_limit: Optional[str] = Field(None, description="CPU limit (e.g., '2')")
    storage: Optional[str] = Field(None, description="Storage allocation (e.g., '10G')")
    additional_settings: Optional[Dict[str, Any]] = Field(None, description="Additional game-specific settings")

class GameServerActionRequest(BaseModel):
    game_type: str
    server_name: str
    action: str  # start, stop, restart, status

class InfrastructureActionRequest(BaseModel):
    action_type: str = Field(description="Type of action to perform (create, read, update, delete)")
    resource_type: str = Field(description="Type of resource to act on (firewall_rule, nat, vpn, etc)")
    parameters: Dict[str, Any] = Field(description="Parameters for the action")

class TaskResponse(BaseModel):
    task_id: str
    status: str = "queued"
    message: str

class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# Function to initialize components
def initialize_components():
    """Initialize all the components needed for the application"""
    
    logger.info("Initializing Ollama interface")
    ollama = OllamaInterface(
        llm_model=Config.OLLAMA_LLM_MODEL,
        embed_model=Config.OLLAMA_EMBED_MODEL,
        base_url=Config.OLLAMA_BASE_URL
    )
    
    logger.info("Initializing vector store")
    vector_store = VectorStore(
        embeddings=ollama.get_embeddings(),
        persist_directory=Config.VECTOR_DB_DIR
    )
    
    logger.info("Initializing infrastructure agent")
    infra_agent = InfrastructureAgent(
        opnsense_api_url=Config.OPNSENSE_API_URL,
        api_key=Config.OPNSENSE_API_KEY,
        api_secret=Config.OPNSENSE_API_SECRET
    )
    
    logger.info("Initializing game server agent")
    game_server_agent = GameServerAgent(
        opnsense_client=None  # This will be handled through the infra agent
    )
    
    return {
        "ollama": ollama,
        "vector_store": vector_store,
        "infra_agent": infra_agent,
        "game_server_agent": game_server_agent
    }

# Initialize components
components = initialize_components()

# API Key validation dependency
async def validate_api_key(x_api_key: str = Header(None)):
    if not Config.MCP_API_KEY or x_api_key != Config.MCP_API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
    return x_api_key

# Create FastAPI app
app = FastAPI(
    title="Booner_Ollama API",
    description="API for Booner_Ollama providing infrastructure as code with LLM capabilities",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Background task function
async def run_task(task_id: str, task_type: str, **kwargs):
    try:
        active_tasks[task_id]["status"] = "running"
        
        if task_type == "llm_generate":
            ollama = components["ollama"]
            prompt_template = """
            {system_prompt}
            
            User: {prompt}
            Assistant:
            """
            
            formatted_prompt = prompt_template.format(
                system_prompt=kwargs.get("system", "You are a helpful assistant."),
                prompt=kwargs["prompt"]
            )
            
            chain = ollama.create_chain("{input}")
            result = chain.invoke({"input": formatted_prompt})
            
            active_tasks[task_id]["status"] = "completed"
            active_tasks[task_id]["result"] = {"response": result}
            
        elif task_type == "game_server_deploy":
            game_server_agent = components["game_server_agent"]
            
            # Convert the kwargs to a GameServerConfig object
            from agents.game_server_agent import GameServerConfig
            config = GameServerConfig(
                game_type=kwargs["game_type"],
                server_name=kwargs["server_name"],
                port=kwargs["port"],
                memory=kwargs["memory"],
                cpu_limit=kwargs.get("cpu_limit"),
                storage=kwargs.get("storage"),
                additional_settings=kwargs.get("additional_settings")
            )
            
            # Deploy the game server
            result = game_server_agent.deploy_game_server(config)
            
            active_tasks[task_id]["status"] = "completed"
            active_tasks[task_id]["result"] = result
            
        elif task_type == "game_server_action":
            game_server_agent = components["game_server_agent"]
            
            action = kwargs["action"]
            game_type = kwargs["game_type"]
            server_name = kwargs["server_name"]
            
            if action == "start":
                result = await game_server_agent.deploy_game_server(game_type, None, server_name)
            elif action == "stop":
                result = await game_server_agent.stop_game_server(game_type, None, server_name)
            elif action == "restart":
                await game_server_agent.stop_game_server(game_type, None, server_name)
                result = await game_server_agent.deploy_game_server(game_type, None, server_name)
            elif action == "status":
                # Implement status check if available
                result = {"status": "unknown", "message": "Status check not implemented yet"}
            else:
                raise ValueError(f"Unknown action: {action}")
            
            active_tasks[task_id]["status"] = "completed"
            active_tasks[task_id]["result"] = result
            
        elif task_type == "infrastructure_action":
            infra_agent = components["infra_agent"]
            
            action = OPNSenseAction(
                action_type=kwargs["action_type"],
                resource_type=kwargs["resource_type"],
                parameters=kwargs["parameters"]
            )
            
            result = infra_agent.execute_opnsense_action(action)
            
            active_tasks[task_id]["status"] = "completed"
            active_tasks[task_id]["result"] = result
            
        else:
            raise ValueError(f"Unknown task type: {task_type}")
            
    except Exception as e:
        logger.error(f"Error in task {task_id}: {str(e)}")
        active_tasks[task_id]["status"] = "failed"
        active_tasks[task_id]["error"] = str(e)

# Bidirectional communication with MCP
async def notify_mcp(event_type: str, data: Dict[str, Any]):
    """Send a notification to the MCP server"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{Config.MCP_URL}/api/notifications",
                headers={"X-API-Key": Config.MCP_API_KEY},
                json={
                    "event_type": event_type,
                    "source": "booner_ollama",
                    "data": data
                },
                timeout=10.0
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"Error notifying MCP: {str(e)}")
        return {"success": False, "error": str(e)}

# API Routes
@app.get("/", dependencies=[Depends(validate_api_key)])
async def root():
    return {"message": "Booner_Ollama API is running"}

@app.get("/health")
async def health_check():
    """Health check endpoint that doesn't require authentication"""
    return {"status": "ok", "version": "0.1.0"}

@app.get("/tasks", dependencies=[Depends(validate_api_key)])
async def get_tasks():
    return {"tasks": active_tasks}

@app.get("/tasks/{task_id}", response_model=TaskStatusResponse, dependencies=[Depends(validate_api_key)])
async def get_task_status(task_id: str):
    if task_id not in active_tasks:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    task = active_tasks[task_id]
    return {
        "task_id": task_id,
        "status": task["status"],
        "result": task.get("result"),
        "error": task.get("error")
    }

# LLM Endpoints
@app.post("/llm/generate", response_model=TaskResponse, dependencies=[Depends(validate_api_key)])
async def llm_generate(request: LLMGenerateRequest, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    active_tasks[task_id] = {"status": "queued"}
    
    background_tasks.add_task(
        run_task,
        task_id=task_id,
        task_type="llm_generate",
        **request.dict()
    )
    
    # Notify MCP that we've started an LLM task
    background_tasks.add_task(
        notify_mcp,
        event_type="llm_task_started",
        data={"task_id": task_id, "model": request.model, "prompt_preview": request.prompt[:100]}
    )
    
    return {
        "task_id": task_id,
        "status": "queued",
        "message": f"LLM generation task queued with model {request.model}"
    }

@app.post("/llm/embed", dependencies=[Depends(validate_api_key)])
async def llm_embed(request: LLMEmbedRequest):
    ollama = components["ollama"]
    embeddings = ollama.get_embeddings()
    
    result = embeddings.embed_query(request.text)
    
    return {"embedding": result}

# Game Server Endpoints
@app.post("/game/deploy", response_model=TaskResponse, dependencies=[Depends(validate_api_key)])
async def deploy_game_server(request: GameServerDeployRequest, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    active_tasks[task_id] = {"status": "queued"}
    
    background_tasks.add_task(
        run_task,
        task_id=task_id,
        task_type="game_server_deploy",
        **request.dict()
    )
    
    # Notify MCP about the deployment task
    background_tasks.add_task(
        notify_mcp,
        event_type="game_server_deployment_started",
        data={"task_id": task_id, "game_type": request.game_type, "server_name": request.server_name}
    )
    
    return {
        "task_id": task_id,
        "status": "queued",
        "message": f"Deploying {request.game_type} server '{request.server_name}'"
    }

@app.post("/game/action", response_model=TaskResponse, dependencies=[Depends(validate_api_key)])
async def game_server_action(request: GameServerActionRequest, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    active_tasks[task_id] = {"status": "queued"}
    
    background_tasks.add_task(
        run_task,
        task_id=task_id,
        task_type="game_server_action",
        **request.dict()
    )
    
    # Notify MCP about the action
    background_tasks.add_task(
        notify_mcp,
        event_type=f"game_server_{request.action}_started",
        data={"task_id": task_id, "game_type": request.game_type, "server_name": request.server_name}
    )
    
    return {
        "task_id": task_id,
        "status": "queued",
        "message": f"{request.action.capitalize()}ing {request.game_type} server '{request.server_name}'"
    }

# Infrastructure Endpoints
@app.post("/infrastructure/action", response_model=TaskResponse, dependencies=[Depends(validate_api_key)])
async def infrastructure_action(request: InfrastructureActionRequest, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    active_tasks[task_id] = {"status": "queued"}
    
    background_tasks.add_task(
        run_task,
        task_id=task_id,
        task_type="infrastructure_action",
        **request.dict()
    )
    
    # Notify MCP about the infrastructure action
    background_tasks.add_task(
        notify_mcp,
        event_type="infrastructure_action_started",
        data={
            "task_id": task_id, 
            "action_type": request.action_type, 
            "resource_type": request.resource_type
        }
    )
    
    return {
        "task_id": task_id,
        "status": "queued",
        "message": f"Performing {request.action_type} on {request.resource_type}"
    }

# Webhook for MCP to notify us of events
@app.post("/webhook", dependencies=[Depends(validate_api_key)])
async def mcp_webhook(request: Request):
    data = await request.json()
    
    event_type = data.get("event_type")
    source = data.get("source")
    event_data = data.get("data", {})
    
    logger.info(f"Received webhook from {source}: {event_type}")
    
    # Handle different types of events from MCP
    if event_type == "mcp_server_started":
        logger.info(f"MCP server started: {event_data.get('server_name')}")
    elif event_type == "mcp_server_stopped":
        logger.info(f"MCP server stopped: {event_data.get('server_name')}")
    elif event_type == "game_server_status_changed":
        logger.info(f"Game server status changed: {event_data.get('server_name')} -> {event_data.get('status')}")
    
    return {"status": "ok"}

# Run the server
def main():
    logger.info("Starting Booner_Ollama API server")
    # Check if we're in Docker environment
    is_docker = os.environ.get('DOCKER_ENV', False)
    
    # If in Docker, don't use reload as it can cause issues with containerized environments
    reload_option = False if is_docker else Config.DEBUG
    
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=reload_option
    )

if __name__ == "__main__":
    main()
