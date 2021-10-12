package summerizers

import (
	"errors"
	"fmt"

	"github.com/johnjones4/model-rocket-telemetry/dashboard/core"
)

type VelocitySummerizer struct {
	mV float64
}

func (s *VelocitySummerizer) Generate(fd []core.DataSegment) error {
	s.mV = 0
	for _, d := range fd {
		//TODO fix mode checking
		if d.Computed.SmoothedVelocity > s.mV && d.Computed.FlightMode == core.ModeAscentPowered {
			s.mV = d.Computed.SmoothedVelocity
		}
	}
	if s.mV == 0 {
		return errors.New("cannot determine max v")
	}
	return nil
}

func (s *VelocitySummerizer) Value() string {
	return fmt.Sprintf("%f m/s", s.mV)
}

func (s *VelocitySummerizer) Name() string {
	return "Max Velocity"
}
