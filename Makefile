DOCKER_REGISTRY = index.docker.io
IMAGE_NAME = pluma-automation
IMAGE_VERSION = latest
IMAGE_ORG = witekio
IMAGE_TAG = $(DOCKER_REGISTRY)/$(IMAGE_ORG)/$(IMAGE_NAME):$(IMAGE_VERSION)
IMAGE_ARMV7_TAG = $(IMAGE_TAG)-armv7

WORKING_DIR := $(shell pwd)
DOCKERFILE_DIR := $(WORKING_DIR)

DOCKER_RUN_CMD :=
DOCKER_RUN_ARGS := -it --rm

ifneq ($(TESTS_CONFIG),)
	DOCKER_RUN_ARGS += -v $(realpath $(TESTS_CONFIG)):/etc/pluma/pluma.yml
endif
ifneq ($(TARGET_CONFIG),)
	DOCKER_RUN_ARGS += -v $(realpath $(TARGET_CONFIG)):/etc/pluma/pluma-target.yml
endif
DOCKER_RUN_PRIVILEGED_ARGS := $(DOCKER_RUN_ARGS) --privileged -v /dev:/dev

.DEFAULT_GOAL := docker-build

install:: ## Install Pluma
		@./install.sh

install-devtools::  ## Install Pluma additional development tools
		@./install_devtools.sh

test:: ## Run the Pluma Automation tests. Tests in tests/rpi are ignored if not on Raspberry Pi
		@./tests/scripts/run_tests.sh $(scope)

test-coverage:: ## Check the code test coverage. Tests in tests/rpi are ignored if not on Raspberry Pi
		@./tests/scripts/run_tests.sh --coverage

typecheck:: ## Run static type checking against the Pluma source code
		pyright pluma

validate:: typecheck test ## Run all checks available

docker-build:: ## Build the docker image
		@echo Building $(IMAGE_TAG)
		@docker build --pull \
			-t $(IMAGE_TAG) $(DOCKERFILE_DIR)

docker-build-arm:: ## Build the docker image
		@echo Building $(IMAGE_ARMV7_TAG)
		@docker build --pull \
			-t $(IMAGE_ARMV7_TAG) -f $(DOCKERFILE_DIR)/Dockerfile-armv7 .

docker-run:: ## Run the docker image
		@docker run $(DOCKER_RUN_ARGS) $(IMAGE_TAG) $(DOCKER_RUN_CMD)

docker-run-arm:: ## Run the docker image
		@docker run $(DOCKER_RUN_ARGS) $(IMAGE_ARMV7_TAG) $(DOCKER_RUN_CMD)

docker-run-privileged:: ## Run the docker image in privileged mode
		@docker run $(DOCKER_RUN_PRIVILEGED_ARGS) $(IMAGE_TAG) $(DOCKER_RUN_CMD)

docker-run-arm-privileged:: ## Run the docker image in privileged mode
		@docker run $(DOCKER_RUN_PRIVILEGED_ARGS) $(IMAGE_ARMV7_TAG) $(DOCKER_RUN_CMD)

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
