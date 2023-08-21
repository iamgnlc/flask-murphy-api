clean:
		./clean.sh

dev:
		flask --app app/main.py --debug run

install:
		pip install -r requirements.txt

lint:
		ruff .

start:
		python server.py

test:
		pytest --verbosity=1 --cov
