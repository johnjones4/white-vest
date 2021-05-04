package dashboard

func NewFlightData() FlightDataConcrete {
	return FlightDataConcrete{0, make([]DataSegment, 0), Coordinate{}}
}

func (f *FlightDataConcrete) IngestNewSegment(bytes []byte) (DataSegment, error) {
	segment, basePressure, origin, err := bytesToDataSegment(f, bytes)
	if err != nil {
		return segment, err
	}
	f.Segments = append(f.Segments, segment)
	f.Base = basePressure
	f.OriginCoordinate = origin
	return segment, nil
}

func (f *FlightDataConcrete) AllSegments() []DataSegment {
	return f.Segments
}

func (f *FlightDataConcrete) BasePressure() float64 {
	return f.Base
}

func (f *FlightDataConcrete) Altitude() []float64 {
	return singleFlightDataElement(f, func(segment DataSegment) float64 {
		return segment.Computed.Altitude
	})
}

func (f *FlightDataConcrete) Velocity() []float64 {
	return singleFlightDataElement(f, func(segment DataSegment) float64 {
		return segment.Computed.Velocity
	})
}

func (f *FlightDataConcrete) Temperature() []float64 {
	return singleFlightDataElement(f, func(segment DataSegment) float64 {
		return segment.Raw.Temperature
	})
}

func (f *FlightDataConcrete) Pressure() []float64 {
	return singleFlightDataElement(f, func(segment DataSegment) float64 {
		return segment.Computed.NormalizedPressure
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
