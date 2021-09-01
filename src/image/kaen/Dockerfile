FROM ubuntu:20.10

ENV KAEN_VERSION 0.0.1
ENV KAEN_BACKEND docker
ENV KAEN_PROVIDER aws

ARG TERRAFORM_VERSION=0.14.7
ARG TERRAFORM=terraform_${TERRAFORM_VERSION}_linux_amd64.zip

ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update \
 && apt-get install -yq --no-install-recommends \
	wget \
	unzip \
	sudo \
	jq \
	ipcalc \
	openssh-client \
	ca-certificates	\
	docker.io \
	# python3 \
	# pip \
 && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /tmp
RUN wget --no-check-certificate https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/${TERRAFORM} \
	&& unzip ${TERRAFORM} \
	&& chmod +x terraform \
	&& mv terraform /usr/local/bin \
	&& rm ${TERRAFORM}

WORKDIR /workspace

RUN mkdir -p /opt/kaen/docker /opt/kaen/k8s
COPY docker/aws /opt/kaen/docker/aws

RUN cd /opt/kaen/docker/aws \
	&& terraform init

COPY sh/ /opt/kaen/
RUN cd /opt/kaen && find . | grep .sh$ | xargs chmod +x
