package summerizers

import (
	"errors"
	"fmt"

	"github.com/johnjones4/model-rocket-telemetry/dashboard/core"
)

type TouchdownSummerizer struct {
	touchdown    core.Coordinate
	touchdownSet bool
}

func (s *TouchdownSummerizer) Generate(fd []core.DataSegment) error {
	s.touchdown = core.Coordinate{}
	s.touchdownSet = false
	for _, d := range fd {
		if !s.touchdownSet && d.Computed.FlightMode == core.ModeRecovery {
			s.touchdown = d.Raw.Coordinate
			s.touchdownSet = true
		}
	}
	if !s.touchdownSet {
		return errors.New("cannot determine touchdown")
	}
	return nil
}

func (s *TouchdownSummerizer) Value() string {
	return fmt.Sprintf("%f/%f", s.touchdown.Lat, s.touchdown.Lon)
}

func (s *TouchdownSummerizer) Name() string {
	return "Touchdown"
}
