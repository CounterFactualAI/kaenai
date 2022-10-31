#!/bin/bash
if [ -z "$(docker images -q 'kaenai/devenv')" ] ; then
	docker build -t kaenai/devenv -f make/container/Dockerfile make/container/ ;
fi

DEV_IMAGE_ID=$(docker images -q "kaenai/devenv")
if [ -z "$DEV_IMAGE_ID" ]
then
	echo "\$DEV_IMAGE_ID is empty"
	exit 1
else
	source $AWS_VARS && \
	docker run -it \
	-u root \
	-e GRANT_SUDO=yes \
	-e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
	-e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
	-e AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION \
	--mount type=bind,src=$(pwd),dst=/kaenai \
	--entrypoint /bin/bash \
	$DEV_IMAGE_ID
	exit 0
fi
