BASE_DOCKER_IMAGE_DEFAULT := library/ubuntu
BASE_DOCKER_TAG_DEFAULT := 20.10

DOCKER_IMAGE_DEFAULT := kaenai/kaen
DOCKER_TAG_DEFAULT := latest

ifneq '$(BASE_DOCKER_IMAGE)' ''
	BASE_DOCKER_IMAGE := $(BASE_DOCKER_IMAGE)
else
	BASE_DOCKER_IMAGE := $(BASE_DOCKER_IMAGE_DEFAULT)
endif

ifneq '$(BASE_DOCKER_TAG)' ''
	BASE_DOCKER_TAG := $(BASE_DOCKER_TAG)
else
	BASE_DOCKER_TAG := $(BASE_DOCKER_TAG_DEFAULT)
endif

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

pull_base:
	docker pull $(BASE_DOCKER_IMAGE):$(BASE_DOCKER_TAG)

clean:
	rm -rf terraform-docker-swarm-aws
	rm -rf docker

build: clean image

rebuild: image

image:
	mkdir -p docker	
	git clone https://github.com/osipov/terraform-docker-swarm-aws.git || true
	rm -rf terraform-docker-swarm-aws/.git terraform-docker-swarm-aws/.gitignore
	mv terraform-docker-swarm-aws docker/aws/
	docker build -t $(DOCKER_IMAGE):$(DOCKER_TAG) .

image_push:
	docker login
	docker push $(DOCKER_IMAGE):$(DOCKER_TAG)

session:
	docker run -it -v $(shell pwd)/.dojo:/workspace/.dojo $(DOCKER_IMAGE):$(DOCKER_TAG) /bin/bash