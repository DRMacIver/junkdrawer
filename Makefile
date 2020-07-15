venv/bin/python:
	virtualenv venv
	venv/bin/pip install -e .

venv/installed: venv/bin/python requirements.txt
	venv/bin/pip install -r requirements.txt
	touch venv/installed


.PHONY: update-requirements
update-requirements: venv/installed
	venv/bin/pip freeze | grep -v '# Editable ' | grep -v '^-e' > requirements.txt
	
