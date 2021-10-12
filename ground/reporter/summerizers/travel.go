package summerizers

import (
	"errors"
	"fmt"

	"github.com/johnjones4/model-rocket-telemetry/dashboard/core"
)

type TravelSummerizer struct {
	distance float64
}

func (s *TravelSummerizer) Generate(fd []core.DataSegment) error {
	s.distance = 0
	for _, d := range fd {
		if d.Computed.Distance > s.distance && d.Computed.FlightMode == core.ModeRecovery {
			s.distance = d.Computed.Distance
		}
	}
	if s.distance == 0 {
		return errors.New("cannot determine travel distance")
	}
	return nil
}

func (s *TravelSummerizer) Value() string {
	return fmt.Sprintf("%f m", s.distance)
}

func (s *TravelSummerizer) Name() string {
	return "Travel Distance"
}
