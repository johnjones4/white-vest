package charts

import "github.com/johnjones4/model-rocket-telemetry/dashboard/core"

func singleFlightDataElement(fd []core.DataSegment, accessor func(core.DataSegment) float64) []float64 {
	data := make([]float64, len(fd))
	for i, segment := range fd {
		data[i] = accessor(segment)
	}
	return data
}
