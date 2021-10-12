package main

import (
	"flag"
	"log"

	"main/summerizers"

	"github.com/johnjones4/model-rocket-telemetry/dashboard/core"
)

type taskSummary struct {
	fs    *flag.FlagSet
	input *string
}

func newTaskSummary() taskSummary {
	tc := taskSummary{
		fs: flag.NewFlagSet("summary", flag.ContinueOnError),
	}
	tc.input = tc.fs.String("input", "", "Input file path")
	return tc
}

func (t taskSummary) FlagSet() *flag.FlagSet {
	return t.fs
}

func (t taskSummary) name() string {
	return t.fs.Name()
}

func (t taskSummary) run() error {
	log.Printf("Reading light data from %s\n", *t.input)
	fd, err := flightDataFromFile(*t.input)
	if err != nil {
		return err
	}

	summerizers := []summerizers.Summarizer{
		&summerizers.ApogeeSummerizer{},
		&summerizers.VelocitySummerizer{},
		&summerizers.TravelSummerizer{},
		&summerizers.OriginSummerizer{},
		&summerizers.TouchdownSummerizer{},
		summerizers.NewModeTimeSummerizer(core.ModeAscentPowered),
		summerizers.NewModeTimeSummerizer(core.ModeAscentUnpowered),
		summerizers.NewModeTimeSummerizer(core.ModeDescentFreefall),
		summerizers.NewModeTimeSummerizer(core.ModeDescentParachute),
	}
	for _, s := range summerizers {
		log.Printf("Calculating %s\n", s.Name())
		err = s.Generate(fd)
		if err != nil {
			return err
		}
	}

	for _, s := range summerizers {
		log.Printf("%s: %s\n", s.Name(), s.Value())
	}

	return nil
}
