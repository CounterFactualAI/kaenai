#!/bin/bash
echo $1
echo $(pwd)

if [ $1 == "env/build" ] ; then
	mkdir -p ../kaenai_env/build
	$PYTHON -m venv ../kaenai_env/build
	source ../kaenai_env/build/bin/activate
	$PYTHON -m pip install --upgrade pip

	pip install --upgrade wheel
	
	deactivate

	exit 0

elif [ $1 == "env/test" ] ; then
	mkdir -p ../kaenai_env/test
	
	$PYTHON -m venv ../kaenai_env/test
	source ../kaenai_env/test/bin/activate	
	$PYTHON -m pip install --upgrade pip
	
	pip install pytest pyspark torch
	pip uninstall $(cd dist && ls -t *.tar.gz | head -c -8)
	pip install $( ls -t dist/*.tar.gz | head -n 1 )
	pip install kaen[all]

	deactivate
	exit 0

elif [ $1 == "clean" ] ; then

	source ../kaenai_env/build/bin/activate

	pushd src/py
	$PYTHON setup.py clean
	popd 

	deactivate

	exit 0

elif [ $1 == "dist" ] ; then

	source ../kaenai_env/build/bin/activate

	pushd src/py
	$PYTHON setup.py sdist -d ../../dist bdist_wheel -d ../../dist
	popd 

	deactivate

	exit 0

elif [ $1 == "test" ] ; then

	source ../kaenai_env/test/bin/activate

	pip install --upgrade $( ls -t dist/*.tar.gz | head -n 1 )
	pytest src/py/test

	deactivate

elif [ $1 == "session" ] ; then

	source ../kaenai_env/test/bin/activate

	pip uninstall $(cd dist && ls -t *.tar.gz | head -c -8)
	pip install --editable src/py
	
	bash

	deactivate

else

	echo "$1: is an unknown command"
	exit 1

fi