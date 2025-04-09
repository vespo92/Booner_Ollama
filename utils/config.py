import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

class Config:
    """Configuration settings for the application"""
    
    # Ollama settings
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_LLM_MODEL = os.getenv("OLLAMA_LLM_MODEL", "mixtral:latest")
    OLLAMA_EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "mxbai-embed-large")
    
    # Vector store settings
    VECTOR_DB_DIR = os.getenv("VECTOR_DB_DIR", "./chroma_db")
    
    # OPNSense settings
    OPNSENSE_API_URL = os.getenv("OPNSENSE_API_URL", "http://localhost:8000")
    OPNSENSE_API_KEY = os.getenv("OPNSENSE_API_KEY", "")
    OPNSENSE_API_SECRET = os.getenv("OPNSENSE_API_SECRET", "")
    
    # Model Context Protocol settings
    MCP_URL = os.getenv("MCP_URL", "http://localhost:5000")
    MCP_API_KEY = os.getenv("MCP_API_KEY", "")
    
    # Application settings
    DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1", "t")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
