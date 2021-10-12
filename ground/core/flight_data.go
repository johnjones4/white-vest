package core

func NewFlightData() FlightDataConcrete {
	return FlightDataConcrete{0, make([]DataSegment, 0), Coordinate{}}
}

func (f *FlightDataConcrete) AppendData(segments []DataSegment) {
	f.Segments = append(f.Segments, segments...)
}

func (f *FlightDataConcrete) SetBasePressure(bp float64) {
	f.Base = bp
}

func (f *FlightDataConcrete) SetOrigin(coord Coordinate) {
	f.OriginCoordinate = coord
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

func (f *FlightDataConcrete) FlightModes() []FlightMode {
	data := make([]FlightMode, len(f.AllSegments()))
	for i, segment := range f.AllSegments() {
		data[i] = segment.Computed.FlightMode
	}
	return data
}
