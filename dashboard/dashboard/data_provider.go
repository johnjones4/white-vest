package dashboard

import (
	"bytes"
	"io/ioutil"
	"time"

	"github.com/jacobsa/go-serial/serial"
)

// DataProvider / DataProviderFile

func NewDataProviderFile(path string) (DataProvider, error) {
	fileBytes, err := ioutil.ReadFile(path)
	if err != nil {
		return nil, err
	}
	dsBytes := make([][]byte, 0)
	rangeStart := 0
	for i, b := range fileBytes {
		if b == '\n' {
			segment := fileBytes[rangeStart:i]
			dsBytes = append(dsBytes, segment)
			rangeStart = i + 1
		}
	}
	return DataProviderFile{dsBytes}, nil
}

func (f DataProviderFile) Stream() <-chan []byte {
	channel := make(chan []byte, 256)
	go func() {
		lastLine := 0
		for {
			time.Sleep(time.Second / 30)
			if lastLine >= len(f.Bytes) {
				return
			}
			channel <- f.Bytes[lastLine]
			lastLine += 1
		}
	}()
	return channel
}

// DataProvider / DataProviderSerial

func NewDataProviderSerial(input string, speed uint) (DataProviderSerial, error) {
	options := serial.OpenOptions{
		PortName:        input,
		BaudRate:        speed,
		DataBits:        8,
		StopBits:        1,
		MinimumReadSize: 4,
	}
	port, err := serial.Open(options)
	return DataProviderSerial{port}, err
}

func (f DataProviderSerial) Stream() <-chan []byte {
	channel := make(chan []byte, 256)
	go func() {
		var buffer bytes.Buffer
		for {
			readBytes := make([]byte, 1024)
			n, _ := f.Port.Read(readBytes)
			for i := 0; i < n; i++ {
				if readBytes[i] == '\n' {
					channel <- buffer.Bytes()
					buffer = *bytes.NewBuffer([]byte{})
				} else {
					buffer.WriteByte(readBytes[i])
				}
			}
		}
	}()
	return channel
}
