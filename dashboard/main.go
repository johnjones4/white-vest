package main

import (
	. "main/dashboard"
	"os"
	"strings"
)

func main() {
	input := os.Args[1]
	var provider DataProvider
	var err error
	if strings.HasPrefix(input, "/dev/") {
		var providerSerial DataProviderSerial
		providerSerial, err = NewDataProviderSerial(input, 9600)
		provider = providerSerial
		//		defer providerSerial.Port.Close()
	} else {
		provider, err = NewDataProviderFile(input)
	}
	if err != nil {
		panic(err)
	}
	df := NewFlightData()
	logger := NewLogger()
	defer logger.Kill()
	err = StartDashboard(provider, &df, logger)
	// err = StartTextLogger(provider, &df, logger)
	if err != nil {
		panic(err)
	}
}
