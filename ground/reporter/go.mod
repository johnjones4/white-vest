module main

go 1.16

replace github.com/johnjones4/model-rocket-telemetry/dashboard/core => ../core

require (
	github.com/cheggaaa/pb/v3 v3.0.8
	github.com/johnjones4/model-rocket-telemetry/dashboard/core v0.0.0-00010101000000-000000000000
	github.com/wcharczuk/go-chart/v2 v2.1.0
	golang.org/x/image v0.0.0-20210628002857-a66eb6448b8d // indirect
)
