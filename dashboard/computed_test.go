package main

import (
	"math"
	"math/rand"
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestBasePressureSet(t *testing.T) {
	segments, avg := makeDataSeries(0)
	b := basePressure(&FlightDataConcrete{
		Base:             0,
		Segments:         segments,
		OriginCoordinate: Coordinate{},
	})
	assert.Equal(t, b, avg)
}

func TestAltitudeNoBase(t *testing.T) {
	alt := altitude(0, RawDataSegment{
		Pressure: rand.Float64(),
	})
	assert.Equal(t, alt, 0.0)
}

func TestAltitudeBase(t *testing.T) {
	alt := altitude(1012, RawDataSegment{
		Pressure: 1010,
	})
	assert.Equal(t, alt, 25868.260058108597)
}

func TestNormalizedPressure(t *testing.T) {
	p := rand.Float64() * 1000
	v := normalizedPressure(RawDataSegment{Pressure: p})
	assert.Equal(t, v, p/100)
}

func TestVelocity(t *testing.T) {
	bp := 1012.0
	segments, _ := makeDataSeries(bp)
	val := (rand.Float64()*20 + 1000) * 100.0
	seg := RawDataSegment{
		Timestamp: float64(len(segments)),
		Pressure:  val,
	}
	vel := velocity(&FlightDataConcrete{
		Base:             0,
		Segments:         segments,
		OriginCoordinate: Coordinate{},
	}, bp, seg)
	vel1 := (altitude(bp, seg) - segments[len(segments)-1].Computed.Altitude) / (seg.Timestamp - segments[len(segments)-1].Raw.Timestamp)
	assert.Equal(t, vel, vel1)
}

func TestYaw(t *testing.T) {
	val := yaw(RawDataSegment{
		Acceleration: XYZ{
			X: 100,
			Y: 110,
			Z: 120,
		},
	})
	assert.Equal(t, val, -39.80557109226519)
}

func TestPitch(t *testing.T) {
	val := pitch(RawDataSegment{
		Acceleration: XYZ{
			X: 100,
			Y: 110,
			Z: 120,
		},
	})
	assert.Equal(t, val, -42.51044707800084)
}

func TestToDegrees(t *testing.T) {
	val := toDegrees(math.Pi)
	assert.Equal(t, val, 180.0)
}

func TestToRadians(t *testing.T) {
	val := toRadians(90)
	assert.Equal(t, val, math.Pi/2)
}

func TestBearing(t *testing.T) {
	origin := Coordinate{
		38.811423646113546,
		-77.054951464077,
	}
	seg := RawDataSegment{
		Coordinate: Coordinate{
			38,
			-77,
		},
	}
	b := bearing(origin, seg)
	assert.Equal(t, b, 179.9862686631269)
}

func TestDistance(t *testing.T) {
	origin := Coordinate{
		38.811423646113546,
		-77.054951464077,
	}
	seg := RawDataSegment{
		Coordinate: Coordinate{
			38,
			-77,
		},
	}
	b := distance(origin, seg)
	assert.Equal(t, b, 90353.15173806295)
}

func TestDataRate(t *testing.T) {
	segments, _ := makeDataSeries(0)
	rate := dataRate(&FlightDataConcrete{
		Segments: segments,
	})
	assert.Equal(t, rate, 1.0)
}

func TestComputeDataSegment(t *testing.T) {
	segments, avg := makeDataSeries(0)
	segment, bp, origin := computeDataSegment(&FlightDataConcrete{
		Segments:         segments,
		OriginCoordinate: Coordinate{37, -76},
	}, RawDataSegment{
		CameraProgress: 1.0,
		Timestamp:      float64(len(segments) + 1),
		Pressure:       1014.0,
		Temperature:    30.0,
		Acceleration:   XYZ{1, 2, 3},
		Magnetic:       XYZ{1, 2, 3},
		Coordinate:     Coordinate{38, -77},
		GPSInfo:        GPSInfo{0.0, 0.0},
		Rssi:           0,
	})
	assert.Equal(t, bp, avg)
	assert.NotEqual(t, origin.Lat, 0.0)
	assert.NotEqual(t, origin.Lon, 0.0)
	assert.NotEqual(t, segment.Altitude, 0.0)
	assert.NotEqual(t, segment.Velocity, 0.0)
	assert.NotEqual(t, segment.Yaw, 0.0)
	assert.NotEqual(t, segment.Pitch, 0.0)
	assert.NotEqual(t, segment.NormalizedPressure, 0.0)
	assert.NotEqual(t, segment.Bearing, 0.0)
	assert.NotEqual(t, segment.Distance, 0.0)
	assert.NotEqual(t, segment.DataRate, 0.0)
}

func makeDataSeries(bp float64) ([]DataSegment, float64) {
	series := make([]DataSegment, 10)
	total := 0.0
	for i := 0; i < len(series); i++ {
		val := rand.Float64()*20 + 1000
		total += val
		series[i] = DataSegment{
			RawDataSegment{
				Timestamp: float64(i),
				Pressure:  val * 100.0,
			},
			ComputedDataSegment{
				NormalizedPressure: val,
				Altitude: altitude(bp, RawDataSegment{
					Pressure: val * 100.0,
				}),
			},
		}
	}
	return series, total / float64(len(series))
}
