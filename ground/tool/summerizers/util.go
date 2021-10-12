package summerizers

import "github.com/johnjones4/model-rocket-telemetry/dashboard/core"

func timeInMode(fd []core.DataSegment, mode core.FlightMode) float64 {
	startTime := -1.0
	for _, d := range fd {
		if d.Computed.FlightMode == mode && startTime < 0 {
			startTime = d.Raw.Timestamp
		} else if d.Computed.FlightMode != mode && startTime > 0 {
			return d.Raw.Timestamp - startTime
		}
	}
	return 0
}
