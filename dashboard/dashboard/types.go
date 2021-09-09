package dashboard

import (
	"io"
	"sync"
)

type FlightMode string

type Coordinate struct {
	Lat float64 `json:"lat"`
	Lon float64 `json:"lon"`
}

type GPSInfo struct {
	Quality float64 `json:"quality"`
	Sats    float64 `json:"sats"`
}

type XYZ struct {
	X float64 `json:"x"`
	Y float64 `json:"y"`
	Z float64 `json:"z"`
}

type RawDataSegment struct {
	WriteProgress float64    `json:"writeProgress"`
	Timestamp     float64    `json:"timestamp"`
	Pressure      float64    `json:"pressure"`
	Temperature   float64    `json:"temperature"`
	Acceleration  XYZ        `json:"acceleration"`
	Magnetic      XYZ        `json:"magnetic"`
	Coordinate    Coordinate `json:"coordinate"`
	GPSInfo       GPSInfo    `json:"gpsInfo"`
	Rssi          int16      `json:"rssi"`
}

type ComputedDataSegment struct {
	Altitude                     float64    `json:"altitude"`
	Velocity                     float64    `json:"velocity"`
	SmoothedVerticalAcceleration float64    `json:"smoothedVerticalAcceleration"`
	Yaw                          float64    `json:"yaw"`
	Pitch                        float64    `json:"pitch"`
	Bearing                      float64    `json:"bearing"`
	Distance                     float64    `json:"distance"`
	DataRate                     float64    `json:"dataRate"`
	SmoothedAltitude             float64    `json:"smoothedAltitude"`
	SmoothedVelocity             float64    `json:"smoothedVelocity"`
	SmoothedPressure             float64    `json:"smoothedPressure"`
	SmoothedTemperature          float64    `json:"smoothedTemperature"`
	FlightMode                   FlightMode `json:"flightMode"`
}

type DataSegment struct {
	Raw      RawDataSegment      `json:"raw"`
	Computed ComputedDataSegment `json:"computed"`
}

type DataProvider interface {
	Stream() <-chan []byte
}

type FlightDataConcrete struct {
	Base             float64
	Segments         []DataSegment
	OriginCoordinate Coordinate
}

type DataProviderFile struct {
	Bytes [][]byte
}

type DataProviderSerial struct {
	Port io.ReadWriteCloser
}

type FlightData interface {
	IngestNewSegment(bytes []byte) ([]DataSegment, error)
	AllSegments() []DataSegment
	BasePressure() float64
	Origin() Coordinate
	Time() []float64
	SmoothedAltitude() []float64
	SmoothedVelocity() []float64
	SmoothedTemperature() []float64
	SmoothedPressure() []float64
	GpsQuality() []float64
	GpsSats() []float64
	Rssi() []float64
}

type Logger struct {
	DataChannel     chan DataSegment
	ContinueRunning bool
	Mutex           sync.Mutex
}

type LoggerControl interface {
	Kill()
	Log(DataSegment)
}
