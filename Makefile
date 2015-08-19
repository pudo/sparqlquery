
install: pyenv/bin/python

pyenv/bin/python:
	virtualenv pyenv
	pyenv/bin/pip install --upgrade pip
	pyenv/bin/pip install wheel nose coverage
	pyenv/bin/pip install -e .

upload: clean install
	pyenv/bin/python setup.py sdist bdist_wheel upload

clean:
	rm -rf pyenv build dist sparqlquery.egg-info
