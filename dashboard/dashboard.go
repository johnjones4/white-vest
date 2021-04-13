package main

import (
	"os"
	"strings"
	"whitevest"
)

func main() {
	input := os.Args[1]
	var provider whitevest.DataProvider
	var err error
	if strings.HasPrefix(input, "/dev/") {
		var providerSerial whitevest.DataProviderSerial
		providerSerial, err = whitevest.NewDataProviderSerial(input, 9600)
		provider = providerSerial
		defer providerSerial.Port.Close()
	} else {
		provider, err = whitevest.NewDataProviderFile(input)
	}
	if err != nil {
		panic(err)
	}
	df := whitevest.NewFlightData()
	logger := whitevest.NewLogger()
	defer logger.Kill()
	err = whitevest.StartDashboard(provider, &df, logger)
	if err != nil {
		panic(err)
	}
}
