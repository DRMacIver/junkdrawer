venv/bin/python:
	virtualenv venv
	venv/bin/pip install -e .

venv/installed: venv/bin/python requirements.txt
	venv/bin/pip install -r requirements.txt
	touch venv/installed

.PHONY: update-requirements
update-requirements: venv/installed
	venv/bin/pip freeze | grep -v '# Editable ' | grep -v '^-e' > requirements.txt
	

.PHONY: test
test: venv/installed
	venv/bin/python -m coverage run --source=src --branch -m pytest tests/ --ff --maxfail=1
	venv/bin/coverage report --show-missing --fail-under=100

.PHONY: format
format: venv/installed
	venv/bin/black src tests
	venv/bin/isort src tests
