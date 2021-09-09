package dashboard

import (
	"embed"
	"fmt"
	"io/fs"
	"net/http"
	"os"
	"path"
	"sync"
	"time"

	ui "github.com/gizak/termui/v3"
	"github.com/gizak/termui/v3/widgets"
	"github.com/gorilla/websocket"
)

const SecondsWindow = 20

//go:embed static/**
var static embed.FS

type staticFS struct {
	content embed.FS
}

func (c staticFS) Open(name string) (fs.File, error) {
	return c.content.Open(path.Join("static", name))
}

func StartTextLogger(p DataProvider, ds FlightData, logger LoggerControl) error {
	if err := ui.Init(); err != nil {
		return err
	}
	defer ui.Close()

	headers := []string{
		"Time",
		"Prog",
		"Pressure",
		"Temp",
		"Accel X",
		"Accel Y",
		"Accel Z",
		"Mag X",
		"Mag Y",
		"Mag Z",
		"Lat",
		"Lon",
		"Sats",
		"Qual",
		"RSSI",
	}

	grid := ui.NewGrid()
	termWidth, termHeight := ui.TerminalDimensions()
	grid.SetRect(0, 0, termWidth, termHeight)

	table := widgets.NewTable()
	table.Title = "Data Stream"
	table.Rows = [][]string{headers}

	errorsui := widgets.NewList()
	errorsui.Title = "Errors"
	errorsui.Rows = []string{}
	errorsui.WrapText = false
	errorsList := make([]error, 0)

	grid.Set(
		ui.NewRow(0.8,
			ui.NewCol(1.0, table),
		),
		ui.NewRow(0.2,
			ui.NewCol(1.0, errorsui),
		),
	)

	uiEvents := ui.PollEvents()
	streamChannel := p.Stream()

	renderTable := func() {
		data := ds.AllSegments()

		if len(data) == 0 {
			ui.Render(grid)
			return
		}
		nRows := (table.Inner.Dy() + 1) / 2
		if nRows <= 0 {
			nRows = 10
		}
		if nRows > len(data)+1 {
			nRows = len(data) + 1
		}
		rows := make([][]string, nRows)
		rows[0] = headers
		for i := 0; i < nRows-1; i++ {
			j := len(data) - nRows + 1 + i
			seg := data[j]
			rows[i+1] = []string{
				fmt.Sprintf("%0.2f", seg.Raw.Timestamp),
				fmt.Sprintf("%0.2f", seg.Raw.WriteProgress),
				fmt.Sprintf("%0.2f", seg.Raw.Pressure),
				fmt.Sprintf("%0.2f", seg.Raw.Temperature),
				fmt.Sprintf("%0.2f", seg.Raw.Acceleration.X),
				fmt.Sprintf("%0.2f", seg.Raw.Acceleration.Y),
				fmt.Sprintf("%0.2f", seg.Raw.Acceleration.Z),
				fmt.Sprintf("%0.2f", seg.Raw.Magnetic.X),
				fmt.Sprintf("%0.2f", seg.Raw.Magnetic.Y),
				fmt.Sprintf("%0.2f", seg.Raw.Magnetic.Z),
				fmt.Sprintf("%0.2f", seg.Raw.Coordinate.Lat),
				fmt.Sprintf("%0.2f", seg.Raw.Coordinate.Lon),
				fmt.Sprintf("%0.2f", seg.Raw.GPSInfo.Sats),
				fmt.Sprintf("%0.2f", seg.Raw.GPSInfo.Quality),
				fmt.Sprintf("%d", seg.Raw.Rssi),
			}
		}
		table.Rows = rows
		ui.Render(grid)
	}

	renderErrors := func() {
		if len(errorsList) == 0 {
			ui.Render(grid)
			return
		}

		nRows := errorsui.Inner.Dy()
		if nRows <= 0 {
			nRows = 10
		}
		if nRows > len(errorsList) {
			nRows = len(errorsList)
		}
		rows := make([]string, nRows)
		for i := 0; i < nRows; i++ {
			j := len(errorsList) - nRows + i
			rows[i] = fmt.Sprint(errorsList[j])
		}
		errorsui.Rows = rows

		ui.Render(grid)
	}

	renderTable()

	for {
		select {
		case e := <-uiEvents:
			switch e.ID {
			case "q", "<C-c>":
				return nil
			}
		case bytes := <-streamChannel:
			latestSegments, err := ds.IngestNewSegment(bytes)
			if err != nil {
				errorsList = append(errorsList, err)
				renderErrors()
			} else {
				renderTable()
				for _, seg := range latestSegments {
					logger.Log(seg)
				}
			}
		}
	}
}

func StartWeb(p DataProvider, ds FlightData, logger LoggerControl) error {
	var mutex sync.Mutex
	var upgrader = websocket.Upgrader{}
	http.HandleFunc("/api/data", func(w http.ResponseWriter, req *http.Request) {
		c, err := upgrader.Upgrade(w, req, nil)
		if err != nil {
			fmt.Println(err)
			return
		}
		defer c.Close()
		mutex.Lock()
		data := ds.AllSegments()
		lastLength := len(data)
		err = c.WriteJSON(data)
		mutex.Unlock()
		if err != nil {
			fmt.Println(err)
			return
		}
		for {
			mutex.Lock()
			data = ds.AllSegments()
			if len(data) > lastLength {
				err = c.WriteJSON(data[lastLength:])
				if err != nil {
					fmt.Println(err)
					mutex.Unlock()
					return
				}
				lastLength = len(data)
			}
			mutex.Unlock()
			time.Sleep(1 * time.Second)
		}
	})
	if os.Getenv("DEV_MODE") == "" {
		http.Handle("/", http.FileServer(http.FS(staticFS{static})))
	} else {
		http.Handle("/", http.FileServer(http.Dir("dashboard/static")))
	}
	go func() {
		streamChannel := p.Stream()
		for {
			bytes := <-streamChannel
			mutex.Lock()
			latestSegments, err := ds.IngestNewSegment(bytes)
			mutex.Unlock()
			if err != nil {
				fmt.Println(err)
			} else {
				for _, seg := range latestSegments {
					logger.Log(seg)
				}
			}
		}
	}()
	return http.ListenAndServe(":8080", nil)
}

// return nil
// if err := ui.Init(); err != nil {
// 	return err
// }
// defer ui.Close()

// altitude := widgets.NewPlot()
// altitude.Data = make([][]float64, 1)

// velocity := widgets.NewPlot()
// velocity.Data = make([][]float64, 1)

// rssi := widgets.NewPlot()
// rssi.Data = make([][]float64, 1)

// temp := widgets.NewSparkline()
// pressure := widgets.NewSparkline()
// tempPress := widgets.NewSparklineGroup(temp, pressure)
// tempPress.Title = "Temperature & Pressure"

// gpsQuality := widgets.NewSparkline()
// gpsSats := widgets.NewSparkline()
// gps := widgets.NewSparklineGroup(gpsQuality, gpsSats)
// gps.Title = "GPS Info"

// bearingDistance := widgets.NewParagraph()
// bearingDistance.Title = "Bearing & Distance"

// pitchYaw := widgets.NewParagraph()
// pitchYaw.Title = "Pitch & Yaw"

// gauge := widgets.NewGauge()

// dataStats := widgets.NewParagraph()
// dataStats.Title = "Signal Stats"

// grid := ui.NewGrid()
// termWidth, termHeight := ui.TerminalDimensions()
// grid.SetRect(0, 0, termWidth, termHeight)

// grid.Set(
// 	ui.NewRow(1.0/2,
// 		ui.NewCol(1.0/3, altitude),
// 		ui.NewCol(1.0/3, velocity),
// 		ui.NewCol(1.0/3, rssi),
// 	),
// 	ui.NewRow(5.0/16,
// 		ui.NewCol(1.0/3, gps),
// 		ui.NewCol(1.0/3, tempPress),
// 		ui.NewCol(1.0/3, dataStats),
// 	),
// 	ui.NewRow(3.0/16,
// 		ui.NewCol(1.0/3, bearingDistance),
// 		ui.NewCol(1.0/3, pitchYaw),
// 		ui.NewCol(1.0/3, gauge),
// 	),
// )

// uiEvents := ui.PollEvents()
// streamChannel := p.Stream()
// ticker := time.NewTicker(time.Second).C
// lastStreamEvent := time.Now()
// lastEventAge := 0.0
// lastLatestSegment := DataSegment{}

// renderDashboard := func() {
// 	if len(ds.AllSegments()) > 1 {
// 		curtime := ds.Time()

// 		altitude.Data[0] = captureEndFrameOfData(curtime, ds.Altitude(), altitude.Inner.Dx()-10, SecondsWindow)
// 		altitude.Title = fmt.Sprintf("Altitude (%.2f)", lastLatestSegment.Computed.Altitude)

// 		velocity.Data[0] = captureEndFrameOfData(curtime, ds.Velocity(), velocity.Inner.Dx()-10, SecondsWindow)
// 		velocity.Title = fmt.Sprintf("Velocity (%.2f)", lastLatestSegment.Computed.Velocity)

// 		temp.Title = fmt.Sprintf("Temperature: %.2f°", lastLatestSegment.Raw.Temperature)
// 		temp.Data = normalize(captureEndFrameOfData(curtime, ds.Temperature(), tempPress.Inner.Dx(), SecondsWindow))

// 		pressure.Title = fmt.Sprintf("Pressure: %.2f mBar", lastLatestSegment.Computed.NormalizedPressure)
// 		pressure.Data = normalize(captureEndFrameOfData(curtime, ds.Pressure(), tempPress.Inner.Dx(), SecondsWindow))

// 		gpsQuality.Title = fmt.Sprintf("GPS Signal Quality: %.2f", lastLatestSegment.Raw.GPSInfo.Quality)
// 		gpsQuality.Data = normalize(captureEndFrameOfData(curtime, ds.GpsQuality(), gps.Inner.Dx(), SecondsWindow))

// 		gpsSats.Title = fmt.Sprintf("GPS Sats: %.0f", lastLatestSegment.Raw.GPSInfo.Sats)
// 		gpsSats.Data = captureEndFrameOfData(curtime, ds.GpsSats(), gps.Inner.Dx(), SecondsWindow)

// 		bearingDistance.Text = fmt.Sprintf("Bearing: %.2f\nDistance: %.2f", lastLatestSegment.Computed.Bearing, lastLatestSegment.Computed.Distance)

// 		pitchYaw.Text = fmt.Sprintf("Pitch: %.2f\nYaw: %.2f", lastLatestSegment.Computed.Pitch, lastLatestSegment.Computed.Yaw)

// 		rssi.Data[0] = captureEndFrameOfData(curtime, ds.Rssi(), rssi.Inner.Dx()-10, SecondsWindow)
// 		rssi.Title = fmt.Sprintf("RSSI (%d)", lastLatestSegment.Raw.Rssi)

// 		gauge.Title = fmt.Sprintf("Mission Time: %s", timeString(lastLatestSegment.Raw.Timestamp))
// 		gauge.Percent = int(100 * lastLatestSegment.Raw.CameraProgress)

// 		receiving := lastEventAge < 5.0
// 		dataStats.Text = fmt.Sprintf("Data Points: %d\nData Rate: %.2f/s\nLast Event Age: %.2fs\nReceiving: %t", len(ds.AllSegments()), lastLatestSegment.Computed.DataRate, lastEventAge, receiving)

// 		ui.Render(grid)
// 	}
// }

// for {
// 	select {
// 	case e := <-uiEvents:
// 		switch e.ID {
// 		case "q", "<C-c>":
// 			return nil
// 		}
// 	case bytes := <-streamChannel:
// 		latestSegments, err := ds.IngestNewSegment(bytes)
// 		if err == nil {
// 			lastStreamEvent = time.Now()
// 			if len(latestSegments) > 0 {
// 				lastLatestSegment = latestSegments[len(latestSegments)-1]
// 				for _, seg := range latestSegments {
// 					logger.Log(seg)
// 				}
// 			}
// 			renderDashboard()
// 		}
// 	case <-ticker:
// 		lastEventAge = float64(time.Since(lastStreamEvent)) / float64(time.Second)
// 		renderDashboard()
// 	}
// }
