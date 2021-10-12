package main

import (
	"encoding/json"
	"fmt"
	"os"
	"path"
	"sync"
	"time"

	"github.com/johnjones4/model-rocket-telemetry/dashboard/core"
)

func dataSegmentToString(ds core.DataSegment) string {
	bytes, err := json.Marshal(ds)
	if err != nil {
		return ""
	} else {
		return string(bytes)
	}
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
		DataChannel:     make(chan core.DataSegment, 100),
		ContinueRunning: true,
		Mutex:           sync.Mutex{},
	}
	go func() {
		logPath, err := generateLogFilePath()
		if err != nil {
			panic(err)
		}
		file, err := os.Create(logPath)
		if err != nil {
			panic(err)
		}
		defer file.Close()
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

func (l *Logger) Log(ds core.DataSegment) {
	l.DataChannel <- ds
}
