package main

import (
	"math/rand"
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestBasePressureSet(t *testing.T) {
	segments, avg := makePressureSeries()
	b := basePressure(&FlightDataConcrete{
		Base:             0,
		Segments:         segments,
		OriginCoordinate: Coordinate{},
	})
	assert.Equal(t, b, avg)
}

func TestAltitude(t *testing.T) {
	//TODO
}

func TestNormalizedPressure(t *testing.T) {
	p := rand.Float64() * 1000
	v := normalizedPressure(RawDataSegment{Pressure: p})
	assert.Equal(t, v, p/100)
}

func TestVelocity(t *testing.T) {
	//TODO
}

func TestYaw(t *testing.T) {
	//TODO
}

func TestPitch(t *testing.T) {
	//TODO
}

func TestToDegrees(t *testing.T) {
	//TODO
}

func TestToRadians(t *testing.T) {
	//TODO
}

func TestBearing(t *testing.T) {
	//TODO
}

func TestDistance(t *testing.T) {
	//TODO
}

func TestDataRate(t *testing.T) {
	//TODO
}

func TestComputeDataSegment(t *testing.T) {
	//TODO
}

func makePressureSeries() ([]DataSegment, float64) {
	series := make([]DataSegment, 10)
	total := 0.0
	for i := 0; i < len(series); i++ {
		val := rand.Float64()
		total += val
		series[i] = DataSegment{
			RawDataSegment{},
			ComputedDataSegment{
				NormalizedPressure: val,
			},
		}
	}
	return series, total / float64(len(series))
}
