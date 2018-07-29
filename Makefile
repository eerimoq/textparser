test:
	python2 setup.py test
	python3 setup.py test
	$(MAKE) test-sdist
	env PYTHONPATH=. python3 examples/hello_world.py
	env PYTHONPATH=. python3 examples/proto3.py
	env PYTHONPATH=. python3 examples/benchmarks/json/errors.py
	env PYTHONPATH=. python3 examples/benchmarks/json/parse_tree.py
	env PYTHONPATH=. python3 examples/benchmarks/json/cpu.py
	codespell -d $$(git ls-files | grep -v \.json)

test-sdist:
	rm -rf dist
	python setup.py sdist
	cd dist && \
	mkdir test && \
	cd test && \
	tar xf ../*.tar.gz && \
	cd textparser-* && \
	python setup.py test

release-to-pypi:
	python setup.py sdist
	python setup.py bdist_wheel --universal
	twine upload dist/*
