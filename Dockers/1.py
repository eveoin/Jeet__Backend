import docker

# Create a Docker client
client = docker.from_env()

# Pull a Docker image
image_name = "nginx:latest"
client.images.pull(image_name)

# Run a Docker container
container = client.containers.run(image_name, detach=True)

# Print container ID
print(f"Container ID: {container.id}")

# Stop and remove the container
container.stop()
container.remove()
