# GPU Acceleration Setup for Booner_Ollama

This document provides instructions for enabling GPU acceleration with Docker for the Booner_Ollama project.

## Prerequisites

- NVIDIA GPU with installed drivers
- Docker and Docker Compose installed

## Installing NVIDIA Container Toolkit

### For Ubuntu/Debian Systems

1. Set up the NVIDIA Container Toolkit repository:

```bash
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
```

2. Update the package lists:

```bash
sudo apt-get update
```

3. Install the NVIDIA Container Toolkit:

```bash
sudo apt-get install -y nvidia-docker2
```

4. Restart the Docker daemon:

```bash
sudo systemctl restart docker
```

### For Other Linux Distributions

For other Linux distributions, please refer to the official NVIDIA documentation:
[NVIDIA Container Toolkit Installation Guide](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)

## Enabling GPU Support in Docker Compose

After installing the NVIDIA Container Toolkit, you need to enable the GPU configuration in the `docker-compose.yml` file:

1. Open the `docker-compose.yml` file:

```bash
nano docker-compose.yml
```

2. Uncomment the GPU deployment section for the ollama service:

```yaml
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: 1
          capabilities: [gpu]
```

3. Save the file and restart your Docker Compose services:

```bash
docker-compose down
docker-compose up -d
```

## Verifying GPU Support

To verify that your containers have access to the GPU:

```bash
docker-compose exec ollama nvidia-smi
```

If properly configured, this should display your GPU information similar to running `nvidia-smi` on the host.

## Running Without GPU Support

If you don't have an NVIDIA GPU or don't want to use GPU acceleration, you can simply use the default configuration with the GPU section commented out. The Ollama service will run using CPU only, which is slower but still functional.

## Troubleshooting

### Common Issues and Solutions

1. **Error: "could not select device driver 'nvidia' with capabilities: [[gpu]]"**
   - This usually means the NVIDIA Container Toolkit is not properly installed or configured
   - Ensure you've completed all the installation steps and restarted Docker

2. **Container fails to start with GPU configuration**
   - Check that your NVIDIA drivers are working properly by running `nvidia-smi` on the host
   - Ensure your GPU is supported by the version of CUDA you're using

3. **Performance issues when using GPU**
   - Monitor GPU usage with `nvidia-smi -l 1` to see real-time utilization
   - Adjust model parameters to better fit your GPU's memory capacity

For additional assistance, please refer to the official NVIDIA Container Toolkit documentation.
