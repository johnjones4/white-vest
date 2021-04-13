.PHONY: generate_test_data run

install:
	GOPATH=$(shell pwd) go get github.com/johnjones4/termui
	GOPATH=$(shell pwd) go get github.com/johnjones4/termui/widgets
	GOPATH=$(shell pwd) go get github.com/jacobsa/go-serial/serial
	GOPATH=$(shell pwd) go get github.com/stretchr/testify/assert

run:
	GOPATH=$(shell pwd) go run . $(source)

generate_test_data:
	GOPATH=$(shell pwd) go run generate_test_data/generate_test_data.go $(file) > data/data.txt

build:
	GOPATH=$(shell pwd) go build -o build/dashboard .

test:
	GOPATH=$(shell pwd) go test .

clean:
	rm -rf build
