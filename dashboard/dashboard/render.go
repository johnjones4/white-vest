package dashboard

import (
	"fmt"
	"time"

	ui "github.com/johnjones4/termui"
	"github.com/johnjones4/termui/widgets"
)

const SecondsWindow = 20

func StartDashboard(p DataProvider, ds FlightData, logger LoggerControl) error {
	if err := ui.Init(); err != nil {
		return err
	}
	defer ui.Close()

	altitude := widgets.NewPlot()
	altitude.Data = make([][]float64, 1)

	velocity := widgets.NewPlot()
	velocity.Data = make([][]float64, 1)

	rssi := widgets.NewPlot()
	rssi.Data = make([][]float64, 1)

	temp := widgets.NewSparkline()
	pressure := widgets.NewSparkline()
	tempPress := widgets.NewSparklineGroup(temp, pressure)
	tempPress.Title = "Temperature & Pressure"

	gpsQuality := widgets.NewSparkline()
	gpsSats := widgets.NewSparkline()
	gps := widgets.NewSparklineGroup(gpsQuality, gpsSats)
	gps.Title = "GPS Info"

	bearingDistance := widgets.NewParagraph()
	bearingDistance.Title = "Bearing & Distance"

	pitchYaw := widgets.NewParagraph()
	pitchYaw.Title = "Pitch & Yaw"

	gauge := widgets.NewGauge()

	dataStats := widgets.NewParagraph()
	dataStats.Title = "Signal Stats"

	grid := ui.NewGrid()
	termWidth, termHeight := ui.TerminalDimensions()
	grid.SetRect(0, 0, termWidth, termHeight)

	grid.Set(
		ui.NewRow(1.0/2,
			ui.NewCol(1.0/3, altitude),
			ui.NewCol(1.0/3, velocity),
			ui.NewCol(1.0/3, rssi),
		),
		ui.NewRow(5.0/16,
			ui.NewCol(1.0/3, gps),
			ui.NewCol(1.0/3, tempPress),
			ui.NewCol(1.0/3, dataStats),
		),
		ui.NewRow(3.0/16,
			ui.NewCol(1.0/3, bearingDistance),
			ui.NewCol(1.0/3, pitchYaw),
			ui.NewCol(1.0/3, gauge),
		),
	)

	uiEvents := ui.PollEvents()
	streamChannel := p.Stream()
	ticker := time.NewTicker(time.Second).C
	lastStreamEvent := time.Now()
	lastEventAge := 0.0
	lastLatestSegment := DataSegment{}

	renderDashboard := func() {
		if len(ds.AllSegments()) > 1 {
			curtime := ds.Time()

			altitude.Data[0] = captureEndFrameOfData(curtime, ds.Altitude(), altitude.Inner.Dx()-10, SecondsWindow)
			altitude.Title = fmt.Sprintf("Altitude (%.2f)", lastLatestSegment.Computed.Altitude)

			velocity.Data[0] = captureEndFrameOfData(curtime, ds.Velocity(), velocity.Inner.Dx()-10, SecondsWindow)
			velocity.Title = fmt.Sprintf("Velocity (%.2f)", lastLatestSegment.Computed.Velocity)

			temp.Title = fmt.Sprintf("Temperature: %.2f°", lastLatestSegment.Raw.Temperature)
			temp.Data = normalize(captureEndFrameOfData(curtime, ds.Temperature(), tempPress.Inner.Dx(), SecondsWindow))

			pressure.Title = fmt.Sprintf("Pressure: %.2f mBar", lastLatestSegment.Computed.NormalizedPressure)
			pressure.Data = normalize(captureEndFrameOfData(curtime, ds.Pressure(), tempPress.Inner.Dx(), SecondsWindow))

			gpsQuality.Title = fmt.Sprintf("GPS Signal Quality: %.2f", lastLatestSegment.Raw.GPSInfo.Quality)
			gpsQuality.Data = normalize(captureEndFrameOfData(curtime, ds.GpsQuality(), gps.Inner.Dx(), SecondsWindow))

			gpsSats.Title = fmt.Sprintf("GPS Sats: %.0f", lastLatestSegment.Raw.GPSInfo.Sats)
			gpsSats.Data = captureEndFrameOfData(curtime, ds.GpsSats(), gps.Inner.Dx(), SecondsWindow)

			bearingDistance.Text = fmt.Sprintf("Bearing: %.2f\nDistance: %.2f", lastLatestSegment.Computed.Bearing, lastLatestSegment.Computed.Distance)

			pitchYaw.Text = fmt.Sprintf("Pitch: %.2f\nYaw: %.2f", lastLatestSegment.Computed.Pitch, lastLatestSegment.Computed.Yaw)

			rssi.Data[0] = captureEndFrameOfData(curtime, ds.Rssi(), rssi.Inner.Dx()-10, SecondsWindow)
			rssi.Title = fmt.Sprintf("RSSI (%d)", lastLatestSegment.Raw.Rssi)

			gauge.Title = fmt.Sprintf("Mission Time: %s", timeString(lastLatestSegment.Raw.Timestamp))
			gauge.Percent = int(100 * lastLatestSegment.Raw.CameraProgress)

			receiving := lastEventAge < 5.0
			dataStats.Text = fmt.Sprintf("Data Points: %d\nData Rate: %.2f/s\nLast Event Age: %.2fs\nReceiving: %t", len(ds.AllSegments()), lastLatestSegment.Computed.DataRate, lastEventAge, receiving)

			ui.Render(grid)
		}
	}

	for {
		select {
		case e := <-uiEvents:
			switch e.ID {
			case "q", "<C-c>":
				return nil
			}
		case bytes := <-streamChannel:
			latestSegment, err := ds.IngestNewSegment(bytes)
			if err == nil {
				lastStreamEvent = time.Now()
				lastLatestSegment = latestSegment
				logger.Log(latestSegment)
				renderDashboard()
			}
		case <-ticker:
			lastEventAge = float64(time.Since(lastStreamEvent)) / float64(time.Second)
			renderDashboard()
		}
	}
}
