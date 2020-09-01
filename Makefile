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
ifneq ($(PROJECT_DIR),)
	DOCKER_RUN_ARGS += -v $(realpath $(PROJECT_DIR)):/root/project

	ifneq ($(PROJECT_SCRIPT),)
		DOCKER_RUN_CMD := python3 /root/project/$(PROJECT_SCRIPT)
	endif
endif
DOCKER_RUN_PRIVILEGED_ARGS := $(DOCKER_RUN_ARGS) --privileged -v /dev:/dev

.DEFAULT_GOAL := docker-build

install:: ## Install Pluma
		@./install.sh

test:: ## Run the all Pluma Automation tests that don't require hardware
		@./internaltests/scripts/run_tests.sh generic

test-all:: ## Run all Pluma Automation tests (generic and RPi specific)
		@./internaltests/scripts/run_tests.sh

test-coverage:: ## Check the code coverage for all tests that don't require hardware
		@./internaltests/scripts/check_test_coverage.sh generic

test-all-coverage:: ## Check the code coverage for all tests (generic and RPi specific)
		@./internaltests/scripts/check_test_coverage.sh

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
