package main

import (
	"flag"
)

type task interface {
	FlagSet() *flag.FlagSet
	name() string
	run() error
}
