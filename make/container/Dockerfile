FROM python:3.9.15-slim

USER root

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update \
 && apt-get install -yq --no-install-recommends \
    make \
    git \
 && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN cd / \
	&& git clone https://github.com/CounterFactualAI/kaenai.git \
	&& cd kaenai \
	# && pip install pytest pyspark twine kaen[all] \
	# && make env/test \
	&& make env/build \
	&& cd / \
	&& find /kaenai_env \
	&& rm -r /kaenai

WORKDIR /kaenai