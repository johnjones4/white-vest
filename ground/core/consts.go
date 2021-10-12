package core

const (
	ModePrelaunch        = "P"
	ModeAscentPowered    = "AP"
	ModeAscentUnpowered  = "AU"
	ModeDescentFreefall  = "DF"
	ModeDescentParachute = "DP"
	ModeRecovery         = "R"
)

const (
	IndexTimestamp     = 0
	IndexPressure      = 1
	IndexTemperature   = 2
	IndexAccelerationX = 3
	IndexAccelerationY = 4
	IndexAccelerationZ = 5
	IndexMagneticX     = 6
	IndexMagneticY     = 7
	IndexMagneticZ     = 8
	IndexCoordinateLat = 9
	IndexCoordinateLon = 10
	IndexGpsQuality    = 11
	IndexGpsSats       = 12
)
