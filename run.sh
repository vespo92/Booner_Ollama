#!/bin/bash

# Function to check if NVIDIA Container Toolkit is installed
check_nvidia_docker() {
    if command -v nvidia-container-cli >/dev/null 2>&1; then
        echo "NVIDIA Container Toolkit found."
        return 0
    else
        echo "NVIDIA Container Toolkit not found."
        return 1
    fi
}

# Function to check if GPU is available
check_gpu() {
    if command -v nvidia-smi >/dev/null 2>&1; then
        echo "NVIDIA GPU detected."
        return 0
    else
        echo "No NVIDIA GPU detected."
        return 1
    fi
}

# Display banner
echo "======================================"
echo "    Booner_Ollama Docker Launcher     "
echo "======================================"

# Check GPU and NVIDIA Container Toolkit
if check_gpu && check_nvidia_docker; then
    echo "GPU support available. Attempting to run with GPU acceleration."
    echo "Starting services with GPU support..."
    docker-compose down
    docker-compose up -d
else
    echo "Running in CPU-only mode."
    echo "For GPU acceleration, please see GPU_SETUP.md for instructions."
    echo "Starting services without GPU support..."
    docker-compose down
    docker-compose -f docker-compose.cpu.yml up -d
fi

echo ""
echo "======================================"
echo "Services started. API available at http://localhost:8000"
echo "To view logs: docker-compose logs -f"
echo "To stop: docker-compose down"
echo "======================================"
