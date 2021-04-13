package whitevest

import (
	"fmt"
	"math"
)

func timeString(seconds float64) string {
	minutes := math.Floor(seconds / 60)
	seconds = (seconds - minutes*60)
	secondsStr := fmt.Sprintf("%.1f", seconds)
	if seconds < 10 {
		secondsStr = fmt.Sprintf("0%.1f", seconds)
	}
	return fmt.Sprintf("%.0f:%s", minutes, secondsStr)
}

func singleFlightDataElement(ds FlightData, accessor func(DataSegment) float64) []float64 {
	data := make([]float64, len(ds.AllSegments()))
	for i, segment := range ds.AllSegments() {
		data[i] = accessor(segment)
	}
	return data
}

func captureEndFrameOfData(time []float64, data []float64, length int, duration float64) []float64 {
	if len(time) < 2 || length <= 0 {
		return []float64{0, 0}
	}
	startIndex := 0
	endTime := time[len(time)-1]
	for i := len(time) - 2; i >= 0 && startIndex == 0; i-- {
		currentDuration := endTime - time[i]
		if currentDuration >= duration {
			startIndex = i
		}
	}
	output := make([]float64, length)
	maxLength := 0
	startTime := time[startIndex]
	for i := startIndex; i < len(data); i++ {
		elapsed := time[i] - startTime
		pcnt := elapsed / duration
		index := int(math.Floor(pcnt * float64(length)))
		if index < len(output) {
			output[index] = data[i]
			maxLength = index + 1
		}
	}
	if maxLength < 2 {
		return []float64{0, 0}
	}
	return output[:maxLength]
}
