package summerizers

import "github.com/johnjones4/model-rocket-telemetry/dashboard/core"

type Summarizer interface {
	Generate(fd []core.DataSegment) error
	Name() string
	Value() string
}
