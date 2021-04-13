package main

import (
	"fmt"
	"os"
	"path"
	"strings"
	"sync"
	"time"
)

func dataSegmentToString(ds DataSegment) string {
	parts := []string{
		fmt.Sprint(ds.Raw.CameraProgress),
		fmt.Sprint(ds.Raw.Timestamp),
		fmt.Sprint(ds.Raw.Pressure),
		fmt.Sprint(ds.Raw.Temperature),
		fmt.Sprint(ds.Raw.Acceleration.X),
		fmt.Sprint(ds.Raw.Acceleration.Y),
		fmt.Sprint(ds.Raw.Acceleration.Z),
		fmt.Sprint(ds.Raw.Magnetic.X),
		fmt.Sprint(ds.Raw.Magnetic.Y),
		fmt.Sprint(ds.Raw.Magnetic.Z),
		fmt.Sprint(ds.Raw.Coordinate.Lat),
		fmt.Sprint(ds.Raw.Coordinate.Lon),
		fmt.Sprint(ds.Raw.GPSInfo.Quality),
		fmt.Sprint(ds.Raw.GPSInfo.Sats),
		fmt.Sprint(ds.Raw.Rssi),
		fmt.Sprint(ds.Computed.Altitude),
		fmt.Sprint(ds.Computed.Velocity),
		fmt.Sprint(ds.Computed.Yaw),
		fmt.Sprint(ds.Computed.Pitch),
		fmt.Sprint(ds.Computed.NormalizedPressure),
		fmt.Sprint(ds.Computed.Bearing),
		fmt.Sprint(ds.Computed.Distance),
		fmt.Sprint(ds.Computed.DataRate),
	}
	return fmt.Sprintln(strings.Join(parts, ","))
}

func generateLogFilePath() (string, error) {
	dirname, err := os.UserHomeDir()
	if err != nil {
		return "", err
	}
	tstamp := time.Now().Unix()
	filename := fmt.Sprintf("whitevest_%d.log", tstamp)
	return path.Join(dirname, filename), nil
}

func NewLogger() LoggerControl {
	logger := Logger{
		DataChannel:     make(chan DataSegment, 100),
		ContinueRunning: true,
		Mutex:           sync.Mutex{},
	}
	go func() {
		logPath, err := generateLogFilePath()
		if err != nil {
			panic(err)
		}
		file, err := os.Create(logPath)
		defer file.Close()
		if err != nil {
			panic(err)
		}
		for {
			ds := <-logger.DataChannel
			_, err = file.WriteString(dataSegmentToString(ds))
			if err != nil {
				panic(err)
			}
			logger.Mutex.Lock()
			if !logger.ContinueRunning {
				return
			}
			logger.Mutex.Unlock()
		}
	}()
	return &logger
}

func (l *Logger) Kill() {
	l.Mutex.Lock()
	l.ContinueRunning = false
	l.Mutex.Unlock()
}

func (l *Logger) Log(ds DataSegment) {
	l.DataChannel <- ds
}
