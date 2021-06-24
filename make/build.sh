#!/bin/bash
echo $1
echo $(pwd)

if [ $1 == "env/build" ] ; then

	python3 -m venv env/build
	source env/build/bin/activate
	pip install --upgrade wheel
	deactivate

	exit 0

elif [ $1 == "env/test" ] ; then

	python3 -m venv env/test
	source env/test/bin/activate	
	pip install pytest
	pip uninstall $( ls -t dist/*.tar.gz | head -n 1 )
	pip install $( ls -t dist/*.tar.gz | head -n 1 )

	deactivate
	exit 0

elif [ $1 == "clean" ] ; then

	source env/build/bin/activate

	pushd src/py
	python3 setup.py clean
	popd 

	deactivate

	exit 0

elif [ $1 == "dist" ] ; then

	source env/build/bin/activate

	pushd src/py
	python3 setup.py sdist -d ../../dist bdist_wheel -d ../../dist
	popd 

	deactivate

	exit 0

elif [ $1 == "test" ] ; then

	source env/test/bin/activate
	pip install --upgrade $( ls -t dist/*.tar.gz | head -n 1 )
	pytest src/py/test
	deactivate

elif [ $1 == "session" ] ; then

	source env/test/bin/activate
	pip uninstall $( ls -t dist/*.tar.gz | head -n 1 )
	pip install --editable src/py
	
	bash

else

	echo "$1: is an unknown command"
	exit 1

fi