# Docker image parameters
DOCKERHUB_USERNAME := caidam
IMAGE_NAME := private
IMAGE_TAG := kots-consolidation

# Docker commands
copy-env:
	cp ../.env .env

build:
	@echo "Building Docker image..."
	docker build -t $(DOCKERHUB_USERNAME)/$(IMAGE_NAME):$(IMAGE_TAG) .

push:
	@echo "Pushing Docker image to DockerHub..."
	docker push $(DOCKERHUB_USERNAME)/$(IMAGE_NAME):$(IMAGE_TAG)

all: copy-env build push