module main

go 1.16

replace github.com/johnjones4/model-rocket-telemetry/dashboard/core => ../core

require (
	github.com/gizak/termui/v3 v3.1.0
	github.com/gorilla/websocket v1.4.2
	github.com/jacobsa/go-serial v0.0.0-20180131005756-15cf729a72d4
	github.com/johnjones4/model-rocket-telemetry/dashboard/core v0.0.0-00010101000000-000000000000
	github.com/stretchr/testify v1.7.0
	golang.org/x/sys v0.0.0-20211007075335-d3039528d8ac // indirect
)
