DOCKER_REGISTRY = index.docker.io
IMAGE_NAME = automation-lab
IMAGE_VERSION = latest
IMAGE_ORG = witekio
IMAGE_TAG = $(DOCKER_REGISTRY)/$(IMAGE_ORG)/$(IMAGE_NAME):$(IMAGE_VERSION)
IMAGE_ARMV7_TAG = $(IMAGE_TAG)-armv7

WORKING_DIR := $(shell pwd)
DOCKERFILE_DIR := $(WORKING_DIR)

.DEFAULT_GOAL := docker-build

.PHONY: build push tests

install:: ## Install the automation lab
		@./install.sh

docker-build:: ## Build the docker image
		@echo Building $(IMAGE_TAG)
		@docker build --pull \
			-t $(IMAGE_TAG) $(DOCKERFILE_DIR)

docker-build-arm:: ## Build the docker image
		@echo Building $(IMAGE_ARMV7_TAG)
		@docker build --pull \
			-t $(IMAGE_ARMV7_TAG) -f $(DOCKERFILE_DIR)/Dockerfile-armv7 .

docker-run:: ## Run the docker image
		@docker run -it --rm $(IMAGE_TAG)

docker-run-arm:: ## Run the docker image
		@docker run -it --rm $(IMAGE_ARMV7_TAG)

docker-run-privilidged:: ## Run the docker image in privilidged mode
		@docker run --privileged -v /dev:/dev -it --rm $(IMAGE_TAG)

docker-run-arm-privilidged:: ## Run the docker image in privilidged mode
		@docker run --privileged -v /dev:/dev -it --rm $(IMAGE_ARMV7_TAG)

docker-push:: ## Push the docker image to the registry
		@echo Pushing $(IMAGE_TAG)
		@docker push $(IMAGE_TAG)

docker-push-arm:: ## Push the docker image to the registry
		@echo Pushing $(IMAGE_ARMV7_TAG)
		@docker push $(IMAGE_ARMV7_TAG)

# A help target including self-documenting targets (see the awk statement)
define HELP_TEXT
Usage: make [TARGET]... [MAKEVAR1=SOMETHING]...

Available targets:
endef
export HELP_TEXT
help: ## This help target
	@echo
	@echo "$$HELP_TEXT"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / \
		{printf "\033[36m%-30s\033[0m  %s\n", $$1, $$2}' $(MAKEFILE_LIST)
