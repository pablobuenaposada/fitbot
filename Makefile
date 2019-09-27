VIRTUAL_ENV ?= venv
BLACK=$(VIRTUAL_ENV)/bin/black
PIP=$(VIRTUAL_ENV)/bin/pip
PYTHON_VERSION=3.6

clean:
	rm -rf $(VIRTUAL_ENV)
	rm -rf __pycache__

$(VIRTUAL_ENV):
	virtualenv -p python$(PYTHON_VERSION) $(VIRTUAL_ENV)
	$(PIP) install -r requirements.txt

virtualenv: $(VIRTUAL_ENV)

black/check:
	$(BLACK) . --exclude $(VIRTUAL_ENV) --check

black:
	$(BLACK) . --exclude $(VIRTUAL_ENV)
