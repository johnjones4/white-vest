package dashboard

import (
	"math"
)

func basePressure(stream FlightData) float64 {
	pressures := make([]float64, 0)
	for _, segment := range stream.AllSegments() {
		if segment.Computed.SmoothedPressure > 0 {
			pressures = append(pressures, segment.Computed.SmoothedPressure)
		}
		if len(pressures) >= 10 {
			var sum float64 = 0
			for _, v := range pressures {
				sum += v
			}
			return nanSafe(sum / float64(len(pressures)))
		}
	}
	return 0
}

func altitude(bp float64, raw RawDataSegment) float64 {
	if bp == 0 {
		return 0
	}
	return nanSafe(44307.7 * (1 - math.Pow((raw.Pressure/100)/bp, 0.190284)))
}

func normalizedPressure(raw RawDataSegment) float64 {
	return nanSafe(raw.Pressure / 100.0)
}

func velocity(stream FlightData, bp float64, raw RawDataSegment) float64 {
	altitude := altitude(bp, raw)
	segments := stream.AllSegments()
	for i := len(segments) - 1; i >= 0; i -= 1 {
		if segments[i].Computed.Altitude != altitude {
			return nanSafe((altitude - segments[i].Computed.Altitude) / (raw.Timestamp - segments[i].Raw.Timestamp))
		}
	}
	return 0.0
}

func yaw(raw RawDataSegment) float64 {
	return nanSafe(math.Atan2(-1.0*raw.Acceleration.X, raw.Acceleration.Z) * (180.0 / math.Pi))
}

func pitch(raw RawDataSegment) float64 {
	return nanSafe(math.Atan2(-1.0*raw.Acceleration.Y, raw.Acceleration.Z) * (180.0 / math.Pi))
}

func toRadians(degrees float64) float64 {
	return nanSafe(degrees * math.Pi / 180)
}

func toDegrees(radians float64) float64 {
	return nanSafe(radians * 180 / math.Pi)
}

func bearing(origin Coordinate, raw RawDataSegment) float64 {
	if origin.Lat == 0 || origin.Lon == 0 || raw.Coordinate.Lat == 0 || raw.Coordinate.Lon == 0 {
		return 0
	}

	startLat := toRadians(origin.Lat)
	startLng := toRadians(origin.Lon)
	destLat := toRadians(raw.Coordinate.Lon)
	destLng := toRadians(raw.Coordinate.Lon)

	y := math.Sin(destLng-startLng) * math.Cos(destLat)
	x := math.Cos(startLat)*math.Sin(destLat) - math.Sin(startLat)*math.Cos(destLat)*math.Cos(destLng-startLng)
	brng := math.Atan2(y, x)
	brng = toDegrees(brng)
	return nanSafe(math.Mod(brng+360, 360))
}

func distance(origin Coordinate, raw RawDataSegment) float64 {
	if origin.Lat == 0 || origin.Lon == 0 || raw.Coordinate.Lat == 0 || raw.Coordinate.Lon == 0 {
		return 0
	}
	R := 6371e3
	φ1 := origin.Lat * math.Pi / 180
	φ2 := raw.Coordinate.Lat * math.Pi / 180
	Δφ := (raw.Coordinate.Lat - origin.Lat) * math.Pi / 180
	Δλ := (raw.Coordinate.Lon - origin.Lon) * math.Pi / 180
	a := math.Sin(Δφ/2)*math.Sin(Δφ/2) + math.Cos(φ1)*math.Cos(φ2)*math.Sin(Δλ/2)*math.Sin(Δλ/2)
	c := 2 * math.Atan2(math.Sqrt(a), math.Sqrt(1-a))
	return nanSafe(R * c)
}

func dataRate(stream FlightData) float64 {
	totalsMap := make(map[int]float64)
	for _, timestamp := range stream.Time() {
		second := int(math.Floor(timestamp))
		if total, ok := totalsMap[second]; ok {
			totalsMap[second] = total + 1
		} else {
			totalsMap[second] = 1
		}
	}
	total := 0.0
	for _, secondTotal := range totalsMap {
		total += secondTotal
	}
	return nanSafe(total / float64(len(totalsMap)))
}

func averageComputedValue(seconds float64, stream FlightData, raw RawDataSegment, computed ComputedDataSegment, accessor func(seg ComputedDataSegment) float64) float64 {
	total := accessor(computed)
	n := 1.0
	i := len(stream.AllSegments()) - 1
	for i >= 0 && raw.Timestamp-stream.Time()[i] <= seconds {
		total += accessor(stream.AllSegments()[i].Computed)
		n++
		i--
	}
	return nanSafe(total / n)
}

func determineFlightMode(stream FlightData, raw RawDataSegment, computed ComputedDataSegment) FlightMode {
	length := len(stream.AllSegments())
	if length == 0 {
		return ModePrelaunch
	}
	lastMode := stream.AllSegments()[length-1].Computed.FlightMode
	avgVelocity := averageComputedValue(1, stream, raw, computed, func(seg ComputedDataSegment) float64 {
		return seg.SmoothedVelocity
	})
	avgAcceleration := averageComputedValue(1, stream, raw, computed, func(seg ComputedDataSegment) float64 {
		return seg.SmoothedVerticalAcceleration
	})
	if lastMode == ModePrelaunch && avgVelocity > 1 {
		return ModeAscentPowered
	}
	if lastMode == ModeAscentPowered && avgAcceleration < 0 && avgVelocity > 0 {
		return ModeAscentUnpowered
	}
	if (lastMode == ModeAscentPowered || lastMode == ModeAscentUnpowered) && avgVelocity < 0 {
		return ModeDescentFreefall
	}
	if lastMode == ModeDescentFreefall && math.Abs(avgAcceleration) < 0.5 {
		return ModeDescentParachute
	}
	if (lastMode == ModeDescentFreefall || lastMode == ModeDescentParachute) && math.Abs(avgVelocity) < 0.5 {
		return ModeRecovery
	}
	return lastMode
}

func computeDataSegment(stream FlightData, raw RawDataSegment) (ComputedDataSegment, float64, Coordinate) {
	bp := stream.BasePressure()
	if bp == 0 {
		bp = basePressure(stream)
	}

	origin := stream.Origin()
	if origin.Lat == 0 && origin.Lon == 0 && raw.Coordinate.Lat != 0 && raw.Coordinate.Lon != 0 {
		origin = raw.Coordinate
	}

	alt := altitude(bp, raw)
	vel := velocity(stream, bp, raw)
	press := normalizedPressure(raw)

	smoothedAlt := alt
	smoothedVel := vel
	smoothedVertAccel := 0.0
	smoothedPress := press
	smoothedTemp := raw.Temperature
	s := len(stream.AllSegments())
	if s > 0 {
		alpha := 0.5
		smoothedAlt = smoothed(alpha, alt, stream.SmoothedAltitude()[s-1])
		smoothedVel = smoothed(alpha, vel, stream.SmoothedVelocity()[s-1])
		smoothedPress = smoothed(alpha, press, stream.SmoothedPressure()[s-1])
		smoothedTemp = smoothed(alpha, raw.Temperature, stream.SmoothedTemperature()[s-1])
		smoothedVertAccel = (smoothedVel - stream.SmoothedVelocity()[s-1]) / (raw.Timestamp - stream.Time()[s-1])
	}

	computed := ComputedDataSegment{
		Altitude:                     alt,
		Velocity:                     vel,
		Yaw:                          yaw(raw),
		Pitch:                        pitch(raw),
		Bearing:                      bearing(origin, raw),
		Distance:                     distance(origin, raw),
		DataRate:                     dataRate(stream),
		SmoothedAltitude:             smoothedAlt,
		SmoothedVelocity:             smoothedVel,
		SmoothedPressure:             smoothedPress,
		SmoothedTemperature:          smoothedTemp,
		SmoothedVerticalAcceleration: smoothedVertAccel,
	}

	computed.FlightMode = determineFlightMode(stream, raw, computed)

	return computed, bp, origin
}
