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

rm_base:
	docker image rm $(BASE_DOCKER_IMAGE):$(BASE_DOCKER_TAG)

rm_instances:
	docker ps -a | grep $(DOCKER_IMAGE):$(DOCKER_TAG) | cut -f 1 -d ' ' | xargs docker rm

kill: rm_instances

rm_image: kill
	-docker image rm $(DOCKER_IMAGE):$(DOCKER_TAG)

clean:
	rm -rf terraform-docker-swarm-aws
	rm -rf docker

build: 
	docker build -t $(DOCKER_IMAGE):$(DOCKER_TAG) .

rebuild: clean rm_image rm_base pull_base prep_build build

prep_build: clean
	mkdir -p docker	
	git clone https://github.com/osipov/terraform-docker-swarm-aws.git || true
	rm -rf terraform-docker-swarm-aws/.git terraform-docker-swarm-aws/.gitignore
	mv terraform-docker-swarm-aws docker/aws/

push_image:
	docker login
	docker push $(DOCKER_IMAGE):$(DOCKER_TAG)

publish: push_image	

push: publish

session:
	docker run -it \
	-v /var/run/docker.sock:/var/run/docker.sock:rw \
	-v $(pwd)/tmp:/workspace:rw \
	$(DOCKER_IMAGE):$(DOCKER_TAG) /bin/bash

	docker ps -aql | xargs docker rm