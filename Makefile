activate:
		. .venv/bin/activate

clean:
		./clean.sh

dev:
		flask --app app/main.py --debug run

format:
		black .

freeze:
		pip freeze -l > requirements-dev.txt
		pip freeze -l | grep -ivE "^(pytest|pytest-cov|coverage|ruff|iniconfig|pluggy)==" > requirements.txt

install:
		pip install -r requirements-dev.txt

lint:
		ruff check .

start:
		python server.py

test:
		pytest --verbosity=1 --cov
