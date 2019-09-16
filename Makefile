BLACK=`which black`

clean:
	rm -rf venv
	rm -rf __pycache__

virtualenv: clean
	virtualenv -p python3.6 venv
	venv/bin/pip install -r requirements.txt

black:
	$(BLACK) . --exclude venv
