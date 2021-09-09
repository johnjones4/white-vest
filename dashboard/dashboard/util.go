package dashboard

func singleFlightDataElement(ds FlightData, accessor func(DataSegment) float64) []float64 {
	data := make([]float64, len(ds.AllSegments()))
	for i, segment := range ds.AllSegments() {
		data[i] = accessor(segment)
	}
	return data
}

func smoothed(alpha float64, xt float64, stm1 float64) float64 {
	return alpha*xt + (1-alpha)*stm1
}
