package main

import (
	"math"
)

func basePressure(stream FlightData) float64 {
	pressures := make([]float64, 0)
	for _, segment := range stream.AllSegments() {
		if segment.Computed.NormalizedPressure > 0 {
			pressures = append(pressures, segment.Computed.NormalizedPressure)
		}
		if len(pressures) >= 10 {
			var sum float64 = 0
			for _, v := range pressures {
				sum += v
			}
			return sum / float64(len(pressures))
		}
	}
	return 0
}

func altitude(bp float64, raw RawDataSegment) float64 {
	if bp == 0 {
		return 0
	}
	return 44307.7 * (1 - math.Pow((raw.Pressure/100)/bp, 0.190284))
}

func normalizedPressure(raw RawDataSegment) float64 {
	return raw.Pressure / 100.0
}

func velocity(stream FlightData, bp float64, raw RawDataSegment) float64 {
	altitude := altitude(bp, raw)
	segments := stream.AllSegments()
	for i := len(segments) - 1; i >= 0; i -= 1 {
		if segments[i].Computed.Altitude != altitude {
			return (altitude - segments[i].Computed.Altitude) / (raw.Timestamp - segments[i].Raw.Timestamp)
		}
	}
	return 0.0
}

func yaw(raw RawDataSegment) float64 {
	return math.Atan2(-1.0*raw.Acceleration.X, raw.Acceleration.Z) * (180.0 / math.Pi)
}

func pitch(raw RawDataSegment) float64 {
	return math.Atan2(-1.0*raw.Acceleration.Y, raw.Acceleration.Z) * (180.0 / math.Pi)
}

func toRadians(degrees float64) float64 {
	return degrees * math.Pi / 180
}

func toDegrees(radians float64) float64 {
	return radians * 180 / math.Pi
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
	return math.Mod(brng+360, 360)
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
	return R * c
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
	return total / float64(len(totalsMap))
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
	return ComputedDataSegment{
		Altitude:           altitude(bp, raw),
		Velocity:           velocity(stream, bp, raw),
		Yaw:                yaw(raw),
		Pitch:              pitch(raw),
		NormalizedPressure: normalizedPressure(raw),
		Bearing:            bearing(origin, raw),
		Distance:           distance(origin, raw),
		DataRate:           dataRate(stream),
	}, bp, origin
}
