all:
	echo TBD

install_deps:
	pip install twine

clean:
	-rm -r build dist
	-rm -r src/py/kaen.egg-info
	-rm -r src/py/build
	make/build.sh $@

env/build:
	make/build.sh $@

env/test: dist
	make/build.sh $@

dist:
	make/build.sh $@

test: env/test 
	make/build.sh $@

session: env/test 
	make/build.sh $@

pip:
	twine upload --repository pypi dist/*

