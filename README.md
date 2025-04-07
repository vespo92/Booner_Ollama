# Booner_Ollama

A local AI-powered Infrastructure as a Service (IaaS) system using Ollama models for launching applications, game servers, and other infrastructure through agentic demands.

## Architecture

This system is designed to run across multiple machines:

1. **Ollama Server Machine**: Runs the Ollama models for LLM inference and embeddings
   - Hardware: Ryzen 7 5700x3d, 64GB RAM, 1TB NVME, RTX 4070 Ti Super

2. **Model Context Protocol Server**: Manages context and coordinates between agents
   - Hardware: Ryzen 9 3900x, 64GB RAM, 1TB NVME, Quadro P4000

## Features

- Local LLM-powered infrastructure management
- Integration with OPNSense for networking configuration
- Support for deploying various applications:
  - Web applications
  - Database servers
  - Game servers (Minecraft, CS2, Valheim, etc.)
- Vector storage for maintaining context and knowledge
- Distributed architecture for scalability

## Getting Started

### Prerequisites

1. Ollama installed on your inference machine
2. Python 3.8+ installed
3. OPNSense with API access configured
4. Model Context Protocol Server running

### Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/Booner_Ollama.git
   cd Booner_Ollama
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Copy the example environment file and edit it with your settings:
   ```
   cp .env.example .env
   ```

5. Update the `.env` file with your specific configuration:
   - Set the `OLLAMA_BASE_URL` to point to your Ollama server
   - Configure OPNSense API settings
   - Set the Model Context Protocol URL and credentials

### Usage

#### Interactive Mode

Run the application in interactive mode to directly input infrastructure requests:

```
python app.py --interactive
```

This will start a command-line interface where you can enter natural language requests for infrastructure operations.

#### API Mode (Coming Soon)

In the future, you'll be able to run the system as an API server:

```
python app.py
```

## Project Structure

- `agents/`: Contains agent implementations for different tasks
- `models/`: Interfaces for working with LLMs and embedding models
- `utils/`: Utility modules for vector storage, configuration, etc.
- `app.py`: Main application entry point

## Integration with OPN_IaC

This project is designed to work with your OPN_IaC project, which uses a django-ninja stack to talk directly to OPNSense. The agents in this system will communicate with your OPN_IaC API to configure networking and infrastructure.

## Integration with Model Context Protocol

The Model Context Protocol Server manages the context and state for the agents. This system connects to your existing MCP server to maintain conversation context and agent states.

## Adding New Agents

You can add new specialized agents by:

1. Creating a new agent class in the `agents/` directory
2. Registering the agent with the MCP server
3. Integrating the agent with the main application flow

Each agent can run on different hardware as needed.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
