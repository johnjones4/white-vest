package main

import (
	"encoding/json"
	"errors"
	"flag"
	"log"
	"main/conversion"
	"os"
)

const (
	DataTypeInboard = "inboard"
)

type taskConvert struct {
	fs       *flag.FlagSet
	input    *string
	output   *string
	dtype    *string
	progress *bool
}

func newTaskConvert() taskConvert {
	tc := taskConvert{
		fs: flag.NewFlagSet("convert", flag.ContinueOnError),
	}
	tc.input = tc.fs.String("input", "", "Input file path")
	tc.dtype = tc.fs.String("type", DataTypeInboard, "Data type (inboard or ground)")
	tc.output = tc.fs.String("output", "converted_flight_data.json", "Output file path")
	tc.progress = tc.fs.Bool("progress", true, "Show progress")
	return tc
}

func (t taskConvert) FlagSet() *flag.FlagSet {
	return t.fs
}

func (t taskConvert) name() string {
	return t.fs.Name()
}

func (t taskConvert) run() error {
	var readerInst conversion.Reader
	switch *t.dtype {
	case DataTypeInboard:
		log.Printf("Will read inboard data from %s\n", *t.input)
		readerInst = conversion.NewInboardReader(*t.input)
	}
	if readerInst == nil {
		return errors.New("data type not supported")
	}

	fd, err := readerInst.Read(*t.progress)
	if err != nil {
		return err
	}

	log.Println("Converting data")
	fdData, err := json.Marshal(fd.AllSegments())
	if err != nil {
		return err
	}

	log.Println("Writing data")
	err = os.WriteFile(*t.output, fdData, 0777)
	if err != nil {
		return err
	}

	return nil
}
