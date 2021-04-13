package whitevest

import (
	"bytes"
	"encoding/base64"
	"encoding/binary"
	"math"
	"strings"
)

const (
	IndexCameraProgress = 0
	IndexTimestamp      = 1
	IndexPressure       = 2
	IndexTemperature    = 3
	IndexAccelerationX  = 4
	IndexAccelerationY  = 5
	IndexAccelerationZ  = 6
	IndexMagneticX      = 7
	IndexMagneticY      = 8
	IndexMagneticZ      = 9
	IndexCoordinateLat  = 10
	IndexCoordinateLon  = 11
	IndexGpsQuality     = 12
	IndexGpsSats        = 13
)

func telemetryFloatFromByteIndex(bytes []byte, index int) float64 {
	start := 8 * index
	end := start + 8
	bits := binary.LittleEndian.Uint64(bytes[start:end])
	float := math.Float64frombits(bits)
	return float
}

func telemetryIntFromBytes(b []byte) int16 {
	buffer := bytes.NewReader(b)
	var val int16
	binary.Read(buffer, binary.LittleEndian, &val)
	return val
}

func bytesToDataSegment(stream FlightData, bytes []byte) (DataSegment, float64, Coordinate, error) {
	parts := strings.Split(string(bytes), ",")
	if parts[0] != "T" || len(parts) != 3 {
		return DataSegment{}, 0, Coordinate{}, nil
	}
	telemetryBytes, err := base64.StdEncoding.DecodeString(parts[1])
	if err != nil {
		return DataSegment{}, 0, Coordinate{}, err
	}
	rssiBytes, err := base64.StdEncoding.DecodeString(parts[2])
	if err != nil {
		return DataSegment{}, 0, Coordinate{}, err
	}

	raw := RawDataSegment{
		CameraProgress: telemetryFloatFromByteIndex(telemetryBytes, IndexCameraProgress),
		Timestamp:      telemetryFloatFromByteIndex(telemetryBytes, IndexTimestamp),
		Pressure:       telemetryFloatFromByteIndex(telemetryBytes, IndexPressure),
		Temperature:    telemetryFloatFromByteIndex(telemetryBytes, IndexTemperature),
		Acceleration: XYZ{
			telemetryFloatFromByteIndex(telemetryBytes, IndexAccelerationX),
			telemetryFloatFromByteIndex(telemetryBytes, IndexAccelerationY),
			telemetryFloatFromByteIndex(telemetryBytes, IndexAccelerationZ),
		},
		Magnetic: XYZ{
			telemetryFloatFromByteIndex(telemetryBytes, IndexMagneticX),
			telemetryFloatFromByteIndex(telemetryBytes, IndexMagneticY),
			telemetryFloatFromByteIndex(telemetryBytes, IndexMagneticZ),
		},
		Coordinate: Coordinate{
			telemetryFloatFromByteIndex(telemetryBytes, IndexCoordinateLat),
			telemetryFloatFromByteIndex(telemetryBytes, IndexCoordinateLon),
		},
		GPSInfo: GPSInfo{
			telemetryFloatFromByteIndex(telemetryBytes, IndexGpsQuality),
			telemetryFloatFromByteIndex(telemetryBytes, IndexGpsSats),
		},
		Rssi: telemetryIntFromBytes(rssiBytes),
	}

	computed, basePressure, origin := computeDataSegment(stream, raw)

	return DataSegment{
		raw,
		computed,
	}, basePressure, origin, nil
}
