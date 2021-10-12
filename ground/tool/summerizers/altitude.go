package summerizers

import (
	"errors"
	"fmt"

	"github.com/johnjones4/model-rocket-telemetry/dashboard/core"
)

type ApogeeSummerizer struct {
	altitude float64
}

func (s *ApogeeSummerizer) Generate(fd []core.DataSegment) error {
	s.altitude = 0
	for _, d := range fd {
		if d.Computed.SmoothedAltitude > s.altitude && d.Computed.FlightMode == core.ModeAscentUnpowered {
			s.altitude = d.Computed.SmoothedAltitude
		}
	}
	if s.altitude == 0 {
		return errors.New("cannot determine apogee")
	}
	return nil
}

func (s *ApogeeSummerizer) Value() string {
	return fmt.Sprintf("%f m", s.altitude)
}

func (s *ApogeeSummerizer) Name() string {
	return "Apogee"
}
