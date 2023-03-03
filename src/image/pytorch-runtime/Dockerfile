#ARG BASE_IMAGE=ubuntu:18.04
ARG PYTHON_VERSION=3.10
ARG BASE_IMAGE=python:${PYTHON_VERSION}-slim
FROM ${BASE_IMAGE} as dev-base

ARG PYTORCH_ARCH=cpu
ARG PYTORCH_VERSION=1.13.1+${PYTORCH_ARCH}
ARG PYTORCH_VISION_VERSION=0.14.1+${PYTORCH_ARCH}
ARG PYTORCH_AUDIO_VERSION=0.13.1+${PYTORCH_ARCH}

RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
				gzip \
				git \
				&& apt-get clean && rm -rf /var/lib/apt/lists/*

RUN pip install torch==${PYTORCH_VERSION} \
								torchvision==${PYTORCH_VISION_VERSION} \
								torchaudio==${PYTORCH_AUDIO_VERSION} \
								--extra-index-url https://download.pytorch.org/whl/${PYTORCH_ARCH}
							
ENV PYTORCH_VERSION ${PYTORCH_VERSION}

RUN mkdir -p /opt/pytorch \ 
		&& cd /opt/pytorch \
		&& git clone https://github.com/pytorch/examples.git

RUN mkdir -p /data/MNIST/raw \
		&& cd /data/MNIST/raw \
		&& curl -O http://yann.lecun.com/exdb/mnist/train-images-idx3-ubyte.gz \
		&& curl -O http://yann.lecun.com/exdb/mnist/train-labels-idx1-ubyte.gz \
		&& curl -O http://yann.lecun.com/exdb/mnist/t10k-images-idx3-ubyte.gz \
		&& curl -O http://yann.lecun.com/exdb/mnist/t10k-labels-idx1-ubyte.gz \
		&& gzip -d *

WORKDIR /workspace
ENTRYPOINT [ "/bin/bash", "-l", "-c" ]