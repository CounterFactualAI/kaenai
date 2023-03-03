SHELL := /bin/bash

PYTHON_VERSION           ?= 3.10
PYTORCH_VERSION          ?= 1.13.1
PYTORCH_VISION_VERSION	 ?= 0.14.1
PYTORCH_AUDIO_VERSION	   ?= 0.13.1

PYTORCH_ARCH						 ?= cpu

DOCKER_REGISTRY          ?= docker.io
DOCKER_ORG							 ?= kaenai
# DOCKER_ORG               ?= $(shell docker info 2>/dev/null | sed '/Username:/!d;s/.* //')
DOCKER_IMAGE             ?= pytorch
DOCKER_FULL_NAME          := $(DOCKER_REGISTRY)/$(DOCKER_ORG)/$(DOCKER_IMAGE)

DOCKER_IMAGE_DEFAULT := pytorch
DOCKER_TAG_DEFAULT := latest

ifneq '$(DOCKER_IMAGE)' ''
	DOCKER_IMAGE := $(DOCKER_IMAGE)
else
	DOCKER_IMAGE := $(DOCKER_IMAGE_DEFAULT)
endif

ifneq '$(DOCKER_TAG)' ''
	DOCKER_TAG := $(DOCKER_TAG)
else
	DOCKER_TAG := $(DOCKER_TAG_DEFAULT)
endif

DOCKER_BUILD = docker build \
									--build-arg PYTHON_VERSION=$(PYTHON_VERSION) \
									--build-arg PYTORCH_VERSION=$(PYTORCH_VERSION) \
									--build-arg PYTORCH_ARCH=$(PYTORCH_ARCH) \
									--build-arg PYTORCH_VISION_VERSION=$(PYTORCH_VISION_VERSION) \
									--build-arg PYTORCH_AUDIO_VERSION=$(PYTORCH_AUDIO_VERSION) \
									-t $(DOCKER_FULL_NAME):$(DOCKER_TAG) \
									-f Dockerfile \
									.

.PHONY: all

all: cpu-rt gpu-rt

cpu-rt: PYTORCH_ARCH := cpu
cpu-rt: BASE_IMAGE := $(BASE_RUNTIME)
cpu-rt: DOCKER_TAG := $(PYTORCH_VERSION)-$(PYTORCH_ARCH)-runtime
cpu-rt: PYTORCH_VERSION := $(PYTORCH_VERSION)+$(PYTORCH_ARCH)
cpu-rt: PYTORCH_VISION_VERSION := $(PYTORCH_VISION_VERSION)+$(PYTORCH_ARCH)
cpu-rt: PYTORCH_AUDIO_VERSION := $(PYTORCH_AUDIO_VERSION)+$(PYTORCH_ARCH)
cpu-rt: 
	$(DOCKER_BUILD)

gpu-rt: PYTORCH_ARCH := cu116
gpu-rt: BASE_IMAGE := $(BASE_RUNTIME)
gpu-rt: DOCKER_TAG := $(PYTORCH_VERSION)-$(PYTORCH_ARCH)-runtime
gpu-rt: PYTORCH_VERSION := $(PYTORCH_VERSION)+$(PYTORCH_ARCH)
gpu-rt: PYTORCH_VISION_VERSION := $(PYTORCH_VISION_VERSION)+$(PYTORCH_ARCH)
gpu-rt: PYTORCH_AUDIO_VERSION := $(PYTORCH_AUDIO_VERSION)+$(PYTORCH_ARCH)
gpu-rt: 
	$(DOCKER_BUILD)



# cpu-rt:
# 	DOCKER_TAG := $(PYTORCH_VERSION)-runtime-cpu

# 	echo docker build \
# 		--build-arg PYTHON_VERSION=$(PYTHON_VERSION) \
# 		--build-arg PYTORCH_VERSION=$(PYTORCH_VERSION) \			
# 		-t $(DOCKER_FULL_NAME):$(DOCKER_TAG) \
# 		-f Dockerfile \
		# .

mnist-cpu:
	docker run -it \
	-u root \
	-e GRANT_SUDO=yes \
	-v $$(pwd):/workspace \
	$(DOCKER_FULL_NAME):$(PYTORCH_VERSION)-$(PYTORCH_ARCH)-runtime \
	'python /opt/pytorch/examples/mnist/main.py'
	
	docker rm $$(docker ps -aq | head -n 1)

mnist-gpu:
	@echo docker run -it \
	-u root \
	-e GRANT_SUDO=yes \
	-v $$(pwd):/workspace \
	kaen/pytorch:1.13.0-cuda11.6-cudnn8-runtime \
	'python /opt/pytorch/examples/mnist/main.py'
	
	docker rm $$(docker ps -aq | head -n 1)

session:
	docker run -it \
	-u root \
	-e GRANT_SUDO=yes \
	-v $$(pwd):/workspace \
	$(DOCKER_FULL_NAME):$(PYTORCH_VERSION)-$(PYTORCH_ARCH)-runtime /bin/bash
	
	docker rm $$(docker ps -aq | head -n 1)

push:
