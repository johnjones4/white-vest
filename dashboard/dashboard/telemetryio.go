package dashboard

import (
	"bytes"
	"encoding/base64"
	"encoding/binary"
	"errors"
	"math"
	"strings"
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

func bytesToDataSegment(stream FlightData, bytes []byte) ([]DataSegment, float64, Coordinate, error) {
	telemetryBytes, rssiBytes, err := decodeTelemetryBytes(bytes)
	if err != nil {
		return nil, 0, Coordinate{}, err
	}

	segments := make([]DataSegment, PointsPerDataFrame)
	var basePressure float64
	var origin Coordinate
	for i := len(segments) - 1; i >= 0; i-- {
		offset := 1 + (i * 13)
		raw := RawDataSegment{
			WriteProgress: telemetryFloatFromByteIndex(telemetryBytes, 0),
			Timestamp:     telemetryFloatFromByteIndex(telemetryBytes, offset+IndexTimestamp),
			Pressure:      telemetryFloatFromByteIndex(telemetryBytes, offset+IndexPressure),
			Temperature:   telemetryFloatFromByteIndex(telemetryBytes, offset+IndexTemperature),
			Acceleration: XYZ{
				telemetryFloatFromByteIndex(telemetryBytes, offset+IndexAccelerationX),
				telemetryFloatFromByteIndex(telemetryBytes, offset+IndexAccelerationY),
				telemetryFloatFromByteIndex(telemetryBytes, offset+IndexAccelerationZ),
			},
			Magnetic: XYZ{
				telemetryFloatFromByteIndex(telemetryBytes, offset+IndexMagneticX),
				telemetryFloatFromByteIndex(telemetryBytes, offset+IndexMagneticY),
				telemetryFloatFromByteIndex(telemetryBytes, offset+IndexMagneticZ),
			},
			Coordinate: Coordinate{
				telemetryFloatFromByteIndex(telemetryBytes, offset+IndexCoordinateLat),
				telemetryFloatFromByteIndex(telemetryBytes, offset+IndexCoordinateLon),
			},
			GPSInfo: GPSInfo{
				telemetryFloatFromByteIndex(telemetryBytes, offset+IndexGpsQuality),
				telemetryFloatFromByteIndex(telemetryBytes, offset+IndexGpsSats),
			},
			Rssi: telemetryIntFromBytes(rssiBytes),
		}

		var computed ComputedDataSegment
		computed, basePressure, origin = computeDataSegment(stream, raw)

		segments[i] = DataSegment{
			raw,
			computed,
		}
	}

	return segments, basePressure, origin, nil
}
