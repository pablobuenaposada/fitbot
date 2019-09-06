clean:
	rm -rf venv

virtualenv: clean
	virtualenv -p python3.6 venv
	venv/bin/pip install -r requirements.txt
