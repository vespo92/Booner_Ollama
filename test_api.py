"""
Test script for the Booner_Ollama API.
This script verifies connectivity with the MCP server.
"""

import asyncio
import httpx
import json
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
API_URL = "http://localhost:8000"
MCP_URL = os.getenv("MCP_URL", "http://localhost:5000")
API_KEY = os.getenv("MCP_API_KEY", "")

async def test_booner_ollama_api():
    """Test the Booner_Ollama API"""
    
    async with httpx.AsyncClient() as client:
        try:
            # Check health endpoint (no auth required)
            logger.info("Testing health endpoint...")
            response = await client.get(f"{API_URL}/health")
            response.raise_for_status()
            logger.info(f"Health check: {response.json()}")
            
            # Test auth with API key
            logger.info("Testing authenticated endpoint...")
            response = await client.get(
                f"{API_URL}/",
                headers={"X-API-Key": API_KEY}
            )
            response.raise_for_status()
            logger.info(f"Authenticated request: {response.json()}")
            
            # Test LLM endpoint
            logger.info("Testing LLM generate endpoint...")
            response = await client.post(
                f"{API_URL}/llm/generate",
                headers={"X-API-Key": API_KEY},
                json={
                    "prompt": "Hello, I'm testing the Booner_Ollama API. Please confirm you can generate text."
                }
            )
            response.raise_for_status()
            task_id = response.json()["task_id"]
            logger.info(f"LLM task queued with ID: {task_id}")
            
            # Wait for task to complete
            for _ in range(10):  # Poll for 10 seconds max
                await asyncio.sleep(1)
                
                task_response = await client.get(
                    f"{API_URL}/tasks/{task_id}",
                    headers={"X-API-Key": API_KEY}
                )
                task_status = task_response.json()
                
                if task_status["status"] in ["completed", "failed"]:
                    logger.info(f"Task completed with status: {task_status['status']}")
                    if "result" in task_status and task_status["result"]:
                        logger.info(f"Response: {task_status['result'].get('response', '')[:100]}...")
                    break
            
            # Test game server deployment endpoint
            logger.info("Testing game server deployment endpoint...")
            response = await client.post(
                f"{API_URL}/game/deploy",
                headers={"X-API-Key": API_KEY},
                json={
                    "game_type": "minecraft",
                    "server_name": "test_server",
                    "port": 25565,
                    "memory": "4G",
                    "cpu_limit": "2",
                    "additional_settings": {
                        "difficulty": "normal",
                        "gamemode": "survival"
                    }
                }
            )
            response.raise_for_status()
            task_id = response.json()["task_id"]
            logger.info(f"Game server deployment task queued with ID: {task_id}")
            
            # Check MCP connectivity
            logger.info("Testing MCP connectivity...")
            try:
                mcp_response = await client.get(
                    f"{MCP_URL}/api/health",
                    timeout=5.0
                )
                logger.info(f"MCP health check: {mcp_response.status_code}")
                if mcp_response.status_code == 200:
                    logger.info("Successfully connected to MCP server!")
                else:
                    logger.warning(f"Unexpected response from MCP server: {mcp_response.status_code}")
            except Exception as e:
                logger.error(f"Failed to connect to MCP server: {e}")
                logger.error("Please ensure MCP server is running and configured correctly.")
            
        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e}")
            logger.error(f"Response: {e.response.text}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    asyncio.run(test_booner_ollama_api())
