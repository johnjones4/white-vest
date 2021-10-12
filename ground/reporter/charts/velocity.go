package charts

import (
	"bytes"
	"os"

	"github.com/johnjones4/model-rocket-telemetry/dashboard/core"
	"github.com/wcharczuk/go-chart/v2"
)

type VelocityChart struct {
	filePath string
}

func NewVelocityChart(f string) ChartTask {
	return VelocityChart{f}
}

func (c VelocityChart) Generate(offsetSeconds float64, fd []core.DataSegment) error {
	graph := chart.Chart{
		Series: []chart.Series{
			chart.ContinuousSeries{
				Name:    "Velocity",
				XValues: singleFlightDataElement(fd, func(d core.DataSegment) float64 { return d.Raw.Timestamp - offsetSeconds }),
				YValues: singleFlightDataElement(fd, func(d core.DataSegment) float64 { return d.Computed.SmoothedVelocity }),
			},
		},
		XAxis: chart.XAxis{
			Name: "Seconds",
		},
		YAxis: chart.YAxis{
			Name: "Meters/Second",
		},
	}

	buffer := bytes.NewBuffer([]byte{})
	err := graph.Render(chart.PNG, buffer)
	if err != nil {
		return err
	}
	err = os.WriteFile(c.filePath, buffer.Bytes(), 0777)
	if err != nil {
		return err
	}

	return nil
}
