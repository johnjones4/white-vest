package main

import (
	"flag"
	. "main/dashboard"
	"strings"
)

const (
	OUTPUT_TYPE_TEXT = "text"
	OUTPUT_TYPE_WEB  = "web"
)

func main() {
	var input = flag.String("input", "", "input (file or device)")
	var output = flag.String("output", OUTPUT_TYPE_WEB, "output style (web, text)")
	flag.Parse()

	var provider DataProvider
	var err error
	if *input == "" {
		flag.Usage()
		return
	} else if strings.HasPrefix(*input, "/dev/") {
		var providerSerial DataProviderSerial
		providerSerial, err = NewDataProviderSerial(*input, 9600)
		provider = providerSerial
	} else {
		provider, err = NewDataProviderFile(*input)
	}
	if err != nil {
		panic(err)
	}
	df := NewFlightData()
	logger := NewLogger()
	defer logger.Kill()
	switch *output {
	case OUTPUT_TYPE_TEXT:
		err = StartTextLogger(provider, &df, logger)
	case OUTPUT_TYPE_WEB:
		err = StartWeb(provider, &df, logger)
	}
	if err != nil {
		panic(err)
	}
}
