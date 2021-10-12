package main

import (
	"flag"
	"log"
	"main/charts"
	"path"
)

type taskChart struct {
	fs     *flag.FlagSet
	input  *string
	output *string
}

func newTaskChart() taskChart {
	tc := taskChart{
		fs: flag.NewFlagSet("chart", flag.ContinueOnError),
	}
	tc.input = tc.fs.String("input", "", "Input file path")
	tc.output = tc.fs.String("output", "", "Output folder")
	return tc
}

func (t taskChart) FlagSet() *flag.FlagSet {
	return t.fs
}

func (t taskChart) name() string {
	return t.fs.Name()
}

func (t taskChart) run() error {
	log.Printf("Reading light data from %s\n", *t.input)
	fd, err := flightDataFromFile(*t.input)
	if err != nil {
		return err
	}

	charts := []charts.ChartTask{
		charts.NewAltitudeChart(path.Join(*t.output, "altitude.png")),
		charts.NewVelocityChart(path.Join(*t.output, "velocity.png")),
	}

	offset := determineOffsetSeconds(fd)

	for _, c := range charts {
		err = c.Generate(offset, fd)
		if err != nil {
			return err
		}
	}

	return nil
}
