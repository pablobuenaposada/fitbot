clean:
	@rm -rf venv

virtualenv: clean
	virtualenv -p python3.6 venv
	. venv/bin/activate; pip install -r requirements.txt
