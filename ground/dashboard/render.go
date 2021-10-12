package main

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
	"github.com/johnjones4/model-rocket-telemetry/dashboard/core"
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

func StartTextLogger(p DataProvider, ds core.FlightData, logger LoggerControl) error {
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
			latestSegments, basePressure, origin, err := bytesToDataSegment(ds, bytes)
			if err != nil {
				errorsList = append(errorsList, err)
				renderErrors()
			} else {
				ds.AppendData(latestSegments)
				ds.SetBasePressure(basePressure)
				ds.SetOrigin(origin)
				renderTable()
				for _, seg := range latestSegments {
					logger.Log(seg)
				}
			}
		}
	}
}

func StartWeb(p DataProvider, ds core.FlightData, logger LoggerControl) error {
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
			latestSegments, basePressure, origin, err := bytesToDataSegment(ds, bytes)
			if err != nil {
				fmt.Println(err)
			} else {
				mutex.Lock()
				ds.AppendData(latestSegments)
				ds.SetBasePressure(basePressure)
				ds.SetOrigin(origin)
				mutex.Unlock()
				for _, seg := range latestSegments {
					logger.Log(seg)
				}
			}
		}
	}()
	return http.ListenAndServe(":8080", nil)
}
