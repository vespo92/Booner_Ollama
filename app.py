from models.ollama_interface import OllamaInterface
from agents.infra_agent import InfrastructureAgent, OPNSenseAction
from utils.config import Config
from utils.vector_store import VectorStore
import logging
import argparse

# Set up logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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
    
    return {
        "ollama": ollama,
        "vector_store": vector_store,
        "infra_agent": infra_agent
    }

def run_interactive_mode(components):
    """Run the application in interactive mode"""
    
    ollama = components["ollama"]
    vector_store = components["vector_store"]
    infra_agent = components["infra_agent"]
    
    # Create a simple chain for infrastructure commands
    infra_template = """
    You are an expert in infrastructure as code. 
    Analyze the user's request and provide the necessary actions to fulfill it.
    
    User request: {request}
    
    Provide your response as structured JSON that can be executed by the infrastructure agent.
    """
    infra_chain = ollama.create_chain(infra_template)
    
    print("Welcome to Booner_Ollama Infrastructure Assistant")
    print("Type 'quit' or 'exit' to end the session")
    
    while True:
        print("\n")
        user_input = input("What infrastructure operations would you like to perform? ")
        
        if user_input.lower() in ["quit", "exit"]:
            break
        
        # Process user input through the LLM chain
        result = infra_chain.invoke({"request": user_input})
        print("\nAI Analysis:")
        print(result)
        
        # In a more complete implementation, we would parse the LLM's response
        # and use it to call the appropriate methods on the infrastructure agent
        print("\nWould you like to execute this plan? (yes/no)")
        confirm = input("> ")
        
        if confirm.lower() in ["yes", "y"]:
            print("\nExecuting infrastructure operations...")
            # Mock execution - in a real implementation, we would parse the LLM's 
            # response and execute the appropriate actions
            print("Operations complete!")

def main():
    """Main entry point for the application"""
    
    parser = argparse.ArgumentParser(description="Booner_Ollama - Local AI for Infrastructure as a Service")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    args = parser.parse_args()
    
    logger.info("Starting Booner_Ollama")
    components = initialize_components()
    
    if args.interactive:
        run_interactive_mode(components)
    else:
        # Default behavior could be to start a web server or API
        print("Starting in server mode... (not implemented yet)")
        # This would be where you'd start FastAPI or another server

if __name__ == "__main__":
    main()
