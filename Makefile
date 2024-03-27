activate:
		. .venv/bin/activate

clean:
		./clean.sh

dev:
		flask --app app/main.py --debug run

format:
		black .

freeze:
		pip freeze -l > requirements.txt

install:
		pip install -r requirements.txt

lint:
		ruff .

start:
		python server.py

pm2:
		pm2 ${COMMAND} ecosystem.config.js

test:
		pytest --verbosity=1 --cov
