package main

import (
	"bytes"
	b64 "encoding/base64"
	"encoding/binary"
	"encoding/csv"
	"fmt"
	"io"
	"math/rand"
	"os"
	"strconv"
	"strings"
)

func main() {
	file := os.Args[1]
	f, err := os.Open(file)
	if err != nil {
		fmt.Println(err)
		return
	}
	defer f.Close()

	csvr := csv.NewReader(f)

	var buf bytes.Buffer
	records := 0
	skipped := 0
	pcnt := 0.0
	for {
		row, err := csvr.Read()
		if err != nil {
			if err == io.EOF {
				return
			}
			fmt.Println(err)
			return
		}
		if skipped == 3 {
			skipped = 0
			if records == 0 {
				_ = binary.Write(&buf, binary.LittleEndian, pcnt)
				pcnt += 0.0001
			}
			for _, el := range row {
				p, err := strconv.ParseFloat(el, 64)
				if err != nil {
					fmt.Println(err)
					return
				} else {
					err := binary.Write(&buf, binary.LittleEndian, p)
					if err != nil {
						fmt.Println(err)
						return
					}
				}
			}
			records++
			if records == 2 {
				sEnc := b64.StdEncoding.EncodeToString(buf.Bytes())

				var buf1 bytes.Buffer
				rssi := int16(rand.Intn(100) * -1)
				err = binary.Write(&buf1, binary.LittleEndian, rssi)
				if err != nil {
					fmt.Println(err)
					return
				}
				sEnc1 := b64.StdEncoding.EncodeToString(buf1.Bytes())

				line := []string{"T", sEnc, sEnc1}

				fmt.Println(strings.Join(line[:], ","))

				records = 0
				buf = *bytes.NewBuffer([]byte{})
			}
		} else {
			skipped++
		}
	}
}
