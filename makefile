venv : 
	python3 -m venv venv
	
activate :
	source /venv/bin/activate

install :
	pip install -r requirements.txt 

integration-test:
	pytest --cov=groundible_client tests/integration_test

unit-test:
	pytest --cov=groundible_client tests/unit_test

all-test:
	pytest --cov=groundible_client tests
