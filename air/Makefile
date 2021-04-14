data:
	mkdir data

air: data
	python3 -m whitevest.bin.air

sensor-test:
	python3 -m whitevest.bin.test_sensors

install: data
	pip3 install -r requirements.txt

install-service:
	ln -s /home/pi/white-vest/air/air.service /etc/systemd/system/air.service
	systemctl daemon-reload
	systemctl enable air.service

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

