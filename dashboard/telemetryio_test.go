package main

import (
	"encoding/base64"
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestTelemetryFloatFromByteIndex(t *testing.T) {
	b64 := "AAAAAAAA8D8AAAAAAAAAQAAAAAAAAAhA"
	data, _ := base64.StdEncoding.DecodeString(b64)
	n := telemetryFloatFromByteIndex(data, 1)
	assert.Equal(t, n, 2.0)
}

func TestTelemetryIntFromBytes(t *testing.T) {
	n := telemetryIntFromBytes([]byte{0x01, 0x00})
	assert.Equal(t, n, int16(1))
}

func TestDecodeTelemetryBytes(t *testing.T) {
	telemetryBytes, rssiBytes, err := decodeTelemetryBytes([]byte("T,wcqhRbbz3T8NAIDUU3JoQGzPymub5/dAAQAM3C/rIkCoKRPINnrovxg/EbSXB+Y/qdDM1YdeMMD+XHTRRRctQAAAAAAAgELAT6wPjfWhL0D2QZYFE2dDQCC4yhMIQ1PAAAAAAAAAAAAAAAAAAAAAAA==,//8="))
	assert.NotNil(t, telemetryBytes)
	assert.NotNil(t, rssiBytes)
	assert.Nil(t, err)
}
