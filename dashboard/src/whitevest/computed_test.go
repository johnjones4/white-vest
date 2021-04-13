package whitevest_test

import (
	"fmt"
	"math/rand"
	"testing"
	"whitevest"
)

func TestNormalizedPressure(t *testing.T) {
	p := rand.Float64() * 1000
	v := whitevest.NormalizedPressure(whitevest.RawDataSegment{Pressure: p})
	if err := assertFloat64(v, p/100); err != nil {
		t.Error(err)
	}
}

func TestBasePressureSet(t *testing.T) {
	segments, avg := makePressureSeries()
	b := whitevest.DetermineBasePressure(&whitevest.FlightDataConcrete{
		Base:             0,
		Segments:         segments,
		OriginCoordinate: whitevest.Coordinate{},
	})
	if err := assertFloat64(b, avg); err != nil {
		t.Error(err)
	}
}

func TestDetermineAltitude(t *testing.T) {

}

func assertFloat64(v1 float64, v2 float64) error {
	if v1 != v2 {
		return fmt.Errorf("%f != %f", v1, v2)
	}
	return nil
}

func makePressureSeries() ([]whitevest.DataSegment, float64) {
	series := make([]whitevest.DataSegment, 10)
	total := 0.0
	for i := 0; i < len(series); i++ {
		val := rand.Float64()
		total += val
		series[i] = whitevest.DataSegment{
			whitevest.RawDataSegment{},
			whitevest.ComputedDataSegment{
				NormalizedPressure: val,
			},
		}
	}
	return series, total / float64(len(series))
}
