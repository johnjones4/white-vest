package dashboard

func NewFlightData() FlightDataConcrete {
	return FlightDataConcrete{0, make([]DataSegment, 0), Coordinate{}}
}

func (f *FlightDataConcrete) IngestNewSegment(bytes []byte) ([]DataSegment, error) {
	segments, basePressure, origin, err := bytesToDataSegment(f, bytes)
	if err != nil {
		return segments, err
	}
	f.Segments = append(f.Segments, segments...)
	f.Base = basePressure
	f.OriginCoordinate = origin
	return segments, nil
}

func (f *FlightDataConcrete) AllSegments() []DataSegment {
	return f.Segments
}

func (f *FlightDataConcrete) BasePressure() float64 {
	return f.Base
}

func (f *FlightDataConcrete) SmoothedAltitude() []float64 {
	return singleFlightDataElement(f, func(segment DataSegment) float64 {
		return segment.Computed.SmoothedAltitude
	})
}

func (f *FlightDataConcrete) SmoothedVelocity() []float64 {
	return singleFlightDataElement(f, func(segment DataSegment) float64 {
		return segment.Computed.SmoothedVelocity
	})
}

func (f *FlightDataConcrete) SmoothedTemperature() []float64 {
	return singleFlightDataElement(f, func(segment DataSegment) float64 {
		return segment.Computed.SmoothedTemperature
	})
}

func (f *FlightDataConcrete) SmoothedPressure() []float64 {
	return singleFlightDataElement(f, func(segment DataSegment) float64 {
		return segment.Computed.SmoothedPressure
	})
}

func (f *FlightDataConcrete) GpsQuality() []float64 {
	return singleFlightDataElement(f, func(segment DataSegment) float64 {
		return segment.Raw.GPSInfo.Quality
	})
}

func (f *FlightDataConcrete) GpsSats() []float64 {
	return singleFlightDataElement(f, func(segment DataSegment) float64 {
		return segment.Raw.GPSInfo.Sats
	})
}

func (f *FlightDataConcrete) Time() []float64 {
	return singleFlightDataElement(f, func(segment DataSegment) float64 {
		return segment.Raw.Timestamp
	})
}

func (f *FlightDataConcrete) Rssi() []float64 {
	return singleFlightDataElement(f, func(segment DataSegment) float64 {
		return float64(segment.Raw.Rssi)
	})
}

func (f *FlightDataConcrete) Origin() Coordinate {
	return f.OriginCoordinate
}
