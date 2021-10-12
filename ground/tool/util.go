package main

import (
	"encoding/json"
	"os"

	"github.com/johnjones4/model-rocket-telemetry/dashboard/core"
)

func flightDataFromFile(input string) ([]core.DataSegment, error) {
	bytes, err := os.ReadFile(input)
	if err != nil {
		return nil, err
	}

	var segs []core.DataSegment
	err = json.Unmarshal(bytes, &segs)
	if err != nil {
		return nil, err
	}

	return segs, err
}

func determineOffsetSeconds(ds []core.DataSegment) float64 {
	for _, d := range ds {
		if d.Computed.FlightMode == core.ModeAscentPowered {
			return d.Raw.Timestamp
		}
	}
	return 0
}
