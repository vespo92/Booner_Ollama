import requests
import json
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class MCPClient:
    """Client for interacting with the Model Context Protocol Server"""
    
    def __init__(self, base_url, api_key=None):
        """
        Initialize the MCP client
        
        Args:
            base_url (str): Base URL for the MCP server
            api_key (str, optional): API key for authentication
        """
        self.base_url = base_url
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json"
        }
        
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"
    
    def get_context(self, context_id: str) -> Dict[str, Any]:
        """
        Get context from the MCP server
        
        Args:
            context_id (str): ID of the context to retrieve
            
        Returns:
            Dict[str, Any]: Context data
        """
        url = f"{self.base_url}/contexts/{context_id}"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting context {context_id}: {e}")
            return {"error": str(e)}
    
    def create_context(self, name: str, initial_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a new context on the MCP server
        
        Args:
            name (str): Name for the new context
            initial_data (Dict[str, Any], optional): Initial data for the context
            
        Returns:
            Dict[str, Any]: Created context data
        """
        url = f"{self.base_url}/contexts"
        payload = {
            "name": name,
            "data": initial_data or {}
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error creating context {name}: {e}")
            return {"error": str(e)}
    
    def update_context(self, context_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing context on the MCP server
        
        Args:
            context_id (str): ID of the context to update
            data (Dict[str, Any]): Data to update
            
        Returns:
            Dict[str, Any]: Updated context data
        """
        url = f"{self.base_url}/contexts/{context_id}"
        payload = {
            "data": data
        }
        
        try:
            response = requests.put(url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error updating context {context_id}: {e}")
            return {"error": str(e)}
    
    def register_agent(self, name: str, capabilities: List[str]) -> Dict[str, Any]:
        """
        Register a new agent with the MCP server
        
        Args:
            name (str): Name for the agent
            capabilities (List[str]): List of agent capabilities
            
        Returns:
            Dict[str, Any]: Registered agent data
        """
        url = f"{self.base_url}/agents"
        payload = {
            "name": name,
            "capabilities": capabilities
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error registering agent {name}: {e}")
            return {"error": str(e)}
