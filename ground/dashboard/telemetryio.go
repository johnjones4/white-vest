package main

import (
	"bytes"
	"encoding/base64"
	"encoding/binary"
	"errors"
	"math"
	"strings"

	"github.com/johnjones4/model-rocket-telemetry/dashboard/core"
)

func telemetryFloatFromByteIndex(bytes []byte, index int) float64 {
	start := 8 * index
	end := start + 8
	if start >= len(bytes) || end >= len(bytes) {
		return 0
	}
	bits := binary.LittleEndian.Uint64(bytes[start:end])
	float := math.Float64frombits(bits)
	return float
}

func telemetryIntFromBytes(b []byte) int16 {
	buffer := bytes.NewReader(b)
	if len(b) != 2 {
		return 0
	}
	var val int16
	binary.Read(buffer, binary.LittleEndian, &val)
	return val
}

func decodeTelemetryBytes(bytes []byte) ([]byte, []byte, error) {
	parts := strings.Split(string(bytes), ",")
	if len(parts) != 3 || parts[0] != "T" {
		return nil, nil, errors.New("bad telemetry")
	}
	telemetryBytes, err := base64.StdEncoding.DecodeString(parts[1])
	if err != nil {
		return nil, nil, err
	}
	rssiBytes, err := base64.StdEncoding.DecodeString(parts[2])
	if err != nil {
		return nil, nil, err
	}
	return telemetryBytes, rssiBytes, nil
}

func bytesToDataSegment(stream core.FlightData, bytes []byte) ([]core.DataSegment, float64, core.Coordinate, error) {
	telemetryBytes, rssiBytes, err := decodeTelemetryBytes(bytes)
	if err != nil {
		return nil, 0, core.Coordinate{}, err
	}

	segments := make([]core.DataSegment, PointsPerDataFrame)
	var basePressure float64
	var origin core.Coordinate
	for i := len(segments) - 1; i >= 0; i-- {
		offset := 1 + (i * 13)
		raw := core.RawDataSegment{
			WriteProgress: telemetryFloatFromByteIndex(telemetryBytes, 0),
			Timestamp:     telemetryFloatFromByteIndex(telemetryBytes, offset+core.IndexTimestamp),
			Pressure:      telemetryFloatFromByteIndex(telemetryBytes, offset+core.IndexPressure),
			Temperature:   telemetryFloatFromByteIndex(telemetryBytes, offset+core.IndexTemperature),
			Acceleration: core.XYZ{
				telemetryFloatFromByteIndex(telemetryBytes, offset+core.IndexAccelerationX),
				telemetryFloatFromByteIndex(telemetryBytes, offset+core.IndexAccelerationY),
				telemetryFloatFromByteIndex(telemetryBytes, offset+core.IndexAccelerationZ),
			},
			Magnetic: core.XYZ{
				telemetryFloatFromByteIndex(telemetryBytes, offset+core.IndexMagneticX),
				telemetryFloatFromByteIndex(telemetryBytes, offset+core.IndexMagneticY),
				telemetryFloatFromByteIndex(telemetryBytes, offset+core.IndexMagneticZ),
			},
			Coordinate: core.Coordinate{
				telemetryFloatFromByteIndex(telemetryBytes, offset+core.IndexCoordinateLat),
				telemetryFloatFromByteIndex(telemetryBytes, offset+core.IndexCoordinateLon),
			},
			GPSInfo: core.GPSInfo{
				telemetryFloatFromByteIndex(telemetryBytes, offset+core.IndexGpsQuality),
				telemetryFloatFromByteIndex(telemetryBytes, offset+core.IndexGpsSats),
			},
			Rssi: telemetryIntFromBytes(rssiBytes),
		}

		var computed core.ComputedDataSegment
		computed, basePressure, origin = core.ComputeDataSegment(stream, raw)

		segments[i] = core.DataSegment{
			raw,
			computed,
		}
	}

	return segments, basePressure, origin, nil
}
