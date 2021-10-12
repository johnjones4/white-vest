package main

import (
	"io"
	"sync"

	"github.com/johnjones4/model-rocket-telemetry/dashboard/core"
)

type Logger struct {
	DataChannel     chan core.DataSegment
	ContinueRunning bool
	Mutex           sync.Mutex
}

type LoggerControl interface {
	Kill()
	Log(core.DataSegment)
}

type DataProvider interface {
	Stream() <-chan []byte
}

type DataProviderFile struct {
	Bytes [][]byte
}

type DataProviderSerial struct {
	Port io.ReadWriteCloser
}
