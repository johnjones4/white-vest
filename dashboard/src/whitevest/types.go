package whitevest

import (
	"io"
	"sync"
)

type Coordinate struct {
	Lat float64
	Lon float64
}

type GPSInfo struct {
	Quality float64
	Sats    float64
}

type XYZ struct {
	X float64
	Y float64
	Z float64
}

type RawDataSegment struct {
	CameraProgress float64
	Timestamp      float64
	Pressure       float64
	Temperature    float64
	Acceleration   XYZ
	Magnetic       XYZ
	Coordinate     Coordinate
	GPSInfo        GPSInfo
	Rssi           int16
}

type ComputedDataSegment struct {
	Altitude           float64
	Velocity           float64
	Yaw                float64
	Pitch              float64
	NormalizedPressure float64
	Bearing            float64
	Distance           float64
	DataRate           float64
}

type DataSegment struct {
	Raw      RawDataSegment
	Computed ComputedDataSegment
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
	IngestNewSegment(bytes []byte) (DataSegment, error)
	AllSegments() []DataSegment
	BasePressure() float64
	Origin() Coordinate
	Time() []float64
	Altitude() []float64
	Velocity() []float64
	Temperature() []float64
	Pressure() []float64
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
