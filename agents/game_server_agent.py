from langchain_core.tools import BaseTool
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
import json
import logging

logger = logging.getLogger(__name__)

class GameServerConfig(BaseModel):
    """Configuration for a game server deployment"""
    game_type: str = Field(description="Type of game server (minecraft, cs2, valheim)")
    server_name: str = Field(description="Name of the server")
    port: int = Field(description="Port to run the server on")
    memory: str = Field(description="Memory allocation (e.g., '4G')")
    cpu_limit: Optional[str] = Field(None, description="CPU limit (e.g., '2')")
    storage: Optional[str] = Field(None, description="Storage allocation (e.g., '10G')")
    additional_settings: Optional[Dict[str, Any]] = Field(None, description="Additional game-specific settings")

class GameServerAgent:
    """Agent specifically for deploying and managing game servers"""
    
    def __init__(self, opnsense_client, docker_endpoint=None):
        """
        Initialize the Game Server Agent
        
        Args:
            opnsense_client: Client for OPNSense API
            docker_endpoint (str, optional): Docker API endpoint
        """
        self.opnsense_client = opnsense_client
        self.docker_endpoint = docker_endpoint
        self.tools = self._create_tools()
    
    def _create_tools(self) -> List[BaseTool]:
        """
        Create tools for the game server agent
        
        Returns:
            List[BaseTool]: List of tools
        """
        
        class DeployMinecraftTool(BaseTool):
            name: str = "deploy_minecraft"
            description: str = "Deploy a Minecraft server"
            
            def _run(self, config: GameServerConfig):
                # In a real implementation, this would deploy a Minecraft server
                return f"Deployed Minecraft server '{config.server_name}' on port {config.port}"
        
        class DeployCS2Tool(BaseTool):
            name: str = "deploy_cs2"
            description: str = "Deploy a Counter-Strike 2 server"
            
            def _run(self, config: GameServerConfig):
                # In a real implementation, this would deploy a CS2 server
                return f"Deployed CS2 server '{config.server_name}' on port {config.port}"
        
        class DeployValheimTool(BaseTool):
            name: str = "deploy_valheim"
            description: str = "Deploy a Valheim server"
            
            def _run(self, config: GameServerConfig):
                # In a real implementation, this would deploy a Valheim server
                return f"Deployed Valheim server '{config.server_name}' on port {config.port}"
        
        return [DeployMinecraftTool(), DeployCS2Tool(), DeployValheimTool()]
    
    def deploy_minecraft_server(self, config: GameServerConfig) -> Dict[str, Any]:
        """
        Deploy a Minecraft server
        
        Args:
            config (GameServerConfig): Server configuration
            
        Returns:
            Dict[str, Any]: Deployment result
        """
        logger.info(f"Deploying Minecraft server: {config.server_name}")
        
        # In a real implementation, this would:
        # 1. Create a Docker container or VM
        # 2. Configure network ports in OPNSense
        # 3. Start the Minecraft server
        
        # Sample configuration for Minecraft
        minecraft_config = {
            "container_name": f"minecraft-{config.server_name}",
            "image": "itzg/minecraft-server",
            "ports": [f"{config.port}:25565"],
            "environment": {
                "EULA": "TRUE",
                "MEMORY": config.memory,
                "SERVER_NAME": config.server_name
            },
            "volumes": [f"minecraft-{config.server_name}-data:/data"]
        }
        
        # Add any additional settings
        if config.additional_settings:
            minecraft_config["environment"].update(config.additional_settings)
        
        # Configure OPNSense firewall rule (mock implementation)
        firewall_rule = {
            "action": "allow",
            "interface": "wan",
            "protocol": "tcp",
            "destination_port": str(config.port),
            "description": f"Minecraft server: {config.server_name}"
        }
        
        # This would call your OPNSense client to create the rule
        # self.opnsense_client.create_firewall_rule(firewall_rule)
        
        return {
            "status": "success",
            "server_id": f"minecraft-{config.server_name}",
            "connection_info": f"Connect to your server at your-public-ip:{config.port}",
            "configuration": minecraft_config
        }
    
    def deploy_cs2_server(self, config: GameServerConfig) -> Dict[str, Any]:
        """
        Deploy a Counter-Strike 2 server
        
        Args:
            config (GameServerConfig): Server configuration
            
        Returns:
            Dict[str, Any]: Deployment result
        """
        logger.info(f"Deploying CS2 server: {config.server_name}")
        
        # Sample configuration for CS2
        cs2_config = {
            "container_name": f"cs2-{config.server_name}",
            "image": "cm2network/cs2",
            "ports": [
                f"{config.port}:27015/tcp",
                f"{config.port}:27015/udp",
                f"{config.port+1}:27020/udp"
            ],
            "environment": {
                "SERVER_HOSTNAME": config.server_name,
                "SERVER_PASSWORD": config.additional_settings.get("password", ""),
                "RCON_PASSWORD": config.additional_settings.get("rcon_password", "changeme")
            },
            "volumes": [f"cs2-{config.server_name}-data:/home/steam/cs2-dedicated"]
        }
        
        # Configure OPNSense firewall rules
        # In a real implementation, this would create the necessary rules
        
        return {
            "status": "success",
            "server_id": f"cs2-{config.server_name}",
            "connection_info": f"Connect to your server at your-public-ip:{config.port}",
            "configuration": cs2_config
        }
    
    def deploy_valheim_server(self, config: GameServerConfig) -> Dict[str, Any]:
        """
        Deploy a Valheim server
        
        Args:
            config (GameServerConfig): Server configuration
            
        Returns:
            Dict[str, Any]: Deployment result
        """
        logger.info(f"Deploying Valheim server: {config.server_name}")
        
        # Sample configuration for Valheim
        valheim_config = {
            "container_name": f"valheim-{config.server_name}",
            "image": "lloesche/valheim-server",
            "ports": [
                f"{config.port}:2456/udp",
                f"{config.port+1}:2457/udp",
                f"{config.port+2}:2458/udp"
            ],
            "environment": {
                "SERVER_NAME": config.server_name,
                "WORLD_NAME": config.additional_settings.get("world_name", "Dedicated"),
                "SERVER_PASS": config.additional_settings.get("password", "changeme")
            },
            "volumes": [f"valheim-{config.server_name}-data:/opt/valheim"]
        }
        
        # Configure OPNSense firewall rules
        # In a real implementation, this would create the necessary rules
        
        return {
            "status": "success",
            "server_id": f"valheim-{config.server_name}",
            "connection_info": f"Connect to your server at your-public-ip:{config.port}",
            "configuration": valheim_config
        }
    
    def deploy_game_server(self, config: GameServerConfig) -> Dict[str, Any]:
        """
        Deploy a game server based on the game type
        
        Args:
            config (GameServerConfig): Server configuration
            
        Returns:
            Dict[str, Any]: Deployment result
        """
        if config.game_type.lower() == "minecraft":
            return self.deploy_minecraft_server(config)
        elif config.game_type.lower() == "cs2":
            return self.deploy_cs2_server(config)
        elif config.game_type.lower() == "valheim":
            return self.deploy_valheim_server(config)
        else:
            return {
                "status": "error",
                "message": f"Unsupported game type: {config.game_type}"
            }
