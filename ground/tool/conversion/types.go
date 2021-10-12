package conversion

import "github.com/johnjones4/model-rocket-telemetry/dashboard/core"

type Reader interface {
	Read(showProgress bool) (core.FlightData, error)
}
