package summerizers

import (
	"fmt"

	"github.com/johnjones4/model-rocket-telemetry/dashboard/core"
)

type ModeTimeSummerizer struct {
	time float64
	mode core.FlightMode
}

func NewModeTimeSummerizer(m core.FlightMode) Summarizer {
	return &ModeTimeSummerizer{0, m}
}

func (s *ModeTimeSummerizer) Generate(fd []core.DataSegment) error {
	s.time = timeInMode(fd, s.mode)
	if s.time == 0 {
		return fmt.Errorf("cannot determine time in %s", s.mode)
	}
	return nil
}

func (s *ModeTimeSummerizer) Value() string {
	return fmt.Sprintf("%f s", s.time)
}

func (s *ModeTimeSummerizer) Name() string {
	switch s.mode {
	case core.ModePrelaunch:
		return "Prelaunch"
	case core.ModeAscentPowered:
		return "Powered Ascent"
	case core.ModeAscentUnpowered:
		return "Unpowered Ascent"
	case core.ModeDescentFreefall:
		return "Freefall Descent"
	case core.ModeDescentParachute:
		return "Controlled Descent"
	case core.ModeRecovery:
		return "Recovery"
	default:
		return ""
	}
}
