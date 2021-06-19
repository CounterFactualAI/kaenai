install_deps:
	pip install twine

clean:
	-rm -r build dist kaen.egg-info

dist:
	python setup.py sdist bdist_wheel

test:
	pytest test/test_utils.py

pip:
	twine upload --repository pypi dist/*
