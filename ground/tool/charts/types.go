package charts

import "github.com/johnjones4/model-rocket-telemetry/dashboard/core"

type ChartTask interface {
	Generate(offsetSeconds float64, fd []core.DataSegment) error
}
