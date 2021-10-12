package summerizers

import (
	"errors"
	"fmt"

	"github.com/johnjones4/model-rocket-telemetry/dashboard/core"
)

type OriginSummerizer struct {
	origin    core.Coordinate
	originSet bool
}

func (s *OriginSummerizer) Generate(fd []core.DataSegment) error {
	s.origin = core.Coordinate{}
	s.originSet = false
	for _, d := range fd {
		if !s.originSet && d.Computed.FlightMode == core.ModeAscentPowered {
			s.origin = d.Raw.Coordinate
			s.originSet = true
		}
	}
	if !s.originSet {
		return errors.New("cannot determine origin")
	}
	return nil
}

func (s *OriginSummerizer) Value() string {
	return fmt.Sprintf("%f/%f", s.origin.Lat, s.origin.Lon)
}

func (s *OriginSummerizer) Name() string {
	return "Origin"
}
