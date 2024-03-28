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

pm2_start:
		pm2 start ecosystem.config.js

pm2_stop:
		pm2 stop ecosystem.config.js
		pm2 delete flask-murphy-api 

start:
		python server.py

test:
		pytest --verbosity=1 --cov
