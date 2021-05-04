.PHONY: generate_test_data run

OS=$(shell uname)
ARCH=$(shell arch)

install:
	go get ./...
	go get -t ./...

run:
	go run . $(source)

generate_test_data:
	go run generate_test_data/generate_test_data.go $(file) > data/data.txt

build:
	go build -o build/dashboard-$(OS)-$(ARCH) .

test:
	cd dashboard && go test .

clean:
	rm -rf build
