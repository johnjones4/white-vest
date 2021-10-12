package conversion

import (
	"encoding/csv"
	"os"
	"strconv"

	"github.com/cheggaaa/pb/v3"
	"github.com/johnjones4/model-rocket-telemetry/dashboard/core"
)

type InboardReader struct {
	filePath string
}

func NewInboardReader(f string) InboardReader {
	return InboardReader{f}
}

func (i InboardReader) Read(showProgress bool) (core.FlightData, error) {
	f, err := os.Open(i.filePath)
	if err != nil {
		return nil, err
	}
	defer f.Close()
	csvReader := csv.NewReader(f)
	data, err := csvReader.ReadAll()
	if err != nil {
		return nil, err
	}
	fd := core.NewFlightData()
	var bar *pb.ProgressBar
	if showProgress {
		bar = pb.StartNew(len(data))
	}
	for i, row := range data {
		rawSeg := core.RawDataSegment{
			WriteProgress: 0,
			Timestamp:     quietParseFloat(row, core.IndexTimestamp),
			Pressure:      quietParseFloat(row, core.IndexPressure),
			Temperature:   quietParseFloat(row, core.IndexTemperature),
			Acceleration: core.XYZ{
				X: quietParseFloat(row, core.IndexAccelerationX),
				Y: quietParseFloat(row, core.IndexAccelerationY),
				Z: quietParseFloat(row, core.IndexAccelerationZ),
			},
			Magnetic: core.XYZ{
				X: quietParseFloat(row, core.IndexMagneticX),
				Y: quietParseFloat(row, core.IndexMagneticY),
				Z: quietParseFloat(row, core.IndexMagneticZ),
			},
			Coordinate: core.Coordinate{
				Lat: quietParseFloat(row, core.IndexCoordinateLat),
				Lon: quietParseFloat(row, core.IndexCoordinateLon),
			},
			GPSInfo: core.GPSInfo{
				Quality: quietParseFloat(row, core.IndexGpsQuality),
				Sats:    quietParseFloat(row, core.IndexGpsSats),
			},
			Rssi: 0,
		}
		computed, basePressure, origin := core.ComputeDataSegment(&fd, rawSeg)
		fd.AppendData([]core.DataSegment{{
			Raw:      rawSeg,
			Computed: computed,
		}})
		fd.SetBasePressure(basePressure)
		fd.SetOrigin(origin)
		if showProgress {
			bar.SetCurrent(int64(i))
		}
	}
	if showProgress {
		bar.Finish()
	}
	return &fd, nil
}

func quietParseFloat(row []string, i int) float64 {
	f, _ := strconv.ParseFloat(row[i], 64)
	return f
}
