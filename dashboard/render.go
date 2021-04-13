package main

import (
	"fmt"

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
	dataStats.Title = "Data Stats"

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
			ui.NewCol(1.0/3, gauge),
		),
		ui.NewRow(3.0/16,
			ui.NewCol(1.0/3, bearingDistance),
			ui.NewCol(1.0/3, pitchYaw),
			ui.NewCol(1.0/3, dataStats),
		),
	)

	uiEvents := ui.PollEvents()
	streamChannel := p.Stream()
	for {
		select {
		case e := <-uiEvents:
			switch e.ID {
			case "q", "<C-c>":
				return nil
			}
		case bytes := <-streamChannel:
			latestSegment, err := ds.IngestNewSegment(bytes)
			if err == nil && len(ds.AllSegments()) > 1 {
				logger.Log(latestSegment)

				time := ds.Time()

				altitude.Data[0] = captureEndFrameOfData(time, ds.Altitude(), altitude.Inner.Dx()-10, SecondsWindow)
				altitude.Title = fmt.Sprintf("Altitude (%.2f)", latestSegment.Computed.Altitude)

				velocity.Data[0] = captureEndFrameOfData(time, ds.Velocity(), velocity.Inner.Dx()-10, SecondsWindow)
				velocity.Title = fmt.Sprintf("Velocity (%.2f)", latestSegment.Computed.Velocity)

				temp.Title = fmt.Sprintf("Temperature: %.2f°", latestSegment.Raw.Temperature)
				temp.Data = normalize(captureEndFrameOfData(time, ds.Temperature(), tempPress.Inner.Dx(), SecondsWindow))

				pressure.Title = fmt.Sprintf("Pressure: %.2f mBar", latestSegment.Computed.NormalizedPressure)
				pressure.Data = normalize(captureEndFrameOfData(time, ds.Pressure(), tempPress.Inner.Dx(), SecondsWindow))

				gpsQuality.Title = fmt.Sprintf("GPS Signal Quality: %.2f", latestSegment.Raw.GPSInfo.Quality)
				gpsQuality.Data = normalize(captureEndFrameOfData(time, ds.GpsQuality(), gps.Inner.Dx(), SecondsWindow))

				gpsSats.Title = fmt.Sprintf("GPS Sats: %.0f", latestSegment.Raw.GPSInfo.Sats)
				gpsSats.Data = captureEndFrameOfData(time, ds.GpsSats(), gps.Inner.Dx(), SecondsWindow)

				bearingDistance.Text = fmt.Sprintf("Bearing: %.2f\nDistance: %.2f", latestSegment.Computed.Bearing, latestSegment.Computed.Distance)

				pitchYaw.Text = fmt.Sprintf("Pitch: %.2f\nYaw: %.2f", latestSegment.Computed.Pitch, latestSegment.Computed.Yaw)

				rssi.Data[0] = captureEndFrameOfData(time, ds.Rssi(), rssi.Inner.Dx()-10, SecondsWindow)
				rssi.Title = fmt.Sprintf("RSSI (%d)", latestSegment.Raw.Rssi)

				gauge.Title = fmt.Sprintf("Mission Time: %s", timeString(latestSegment.Raw.Timestamp))
				gauge.Percent = int(100 * latestSegment.Raw.CameraProgress)

				dataStats.Text = fmt.Sprintf("Data Points: %d\nData Rate: %.2f/sec", len(ds.AllSegments()), latestSegment.Computed.DataRate)

				ui.Render(grid)
			}
		}
	}
}
