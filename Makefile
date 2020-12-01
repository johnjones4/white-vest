data:
	mkdir data

air: data
	python3 air.py

ground: data
	python3 ground.py

install: data
	pip3 install -r requirements.txt

install-air:
	cp misc/air.service /lib/systemd/system/
	systemctl enable air.service

install-ground:
	cp misc/ground.service /lib/systemd/system/
	systemctl enable ground.service

cleanup:
	isort whitevest/*
	isort tests/*
	black whitevest/*
	black tests/*

lint:
	pylint whitevest/*

test:
	TESTING=true pytest --cov-report=xml --cov=whitevest tests/*

clean:
	\rm -rf build
	\rm -rf dist
	\rm -rf *.egg-info
	\rm .coverage
	\rm coverage.xml

package:
	python3 setup.py sdist bdist_wheel
