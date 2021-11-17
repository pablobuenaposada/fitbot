venv:
	python3 -m venv venv
	venv/bin/pip install -r requirements.txt

format/black: venv
	venv/bin/black --verbose src

format/black-check: venv
	venv/bin/black --verbose src --check

tests: venv format/black-check

docker/build:
	docker build --no-cache	--tag=fitbot .

docker/tests:
	 docker run fitbot /bin/sh -c 'make tests'