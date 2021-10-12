package main

import (
	"log"
	"os"
)

func main() {
	if len(os.Args) < 2 {
		log.Fatal("not enough arguments")
	}
	cmds := []task{
		newTaskConvert(),
		newTaskSummary(),
		newTaskChart(),
	}
	for _, cmd := range cmds {
		if cmd.name() == os.Args[1] {
			cmd.FlagSet().Parse(os.Args[2:])
			err := cmd.run()
			if err != nil {
				log.Panic(err)
			}
			return
		}
	}
}
