.PHONY: generate_test_data run

OS=$(shell uname)
ARCH=$(shell arch)

install:
	go get ./...
	go get -t ./...

run:
	go run . $(source)

build:
	go build -o build/white-vest-dashboard-$(OS)-$(ARCH) .

test:
	go test .

clean:
	rm -rf build
