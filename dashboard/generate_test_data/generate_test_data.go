package main

import (
	"fmt"
	"os"
	"encoding/csv"
	"io"
	"strconv"
	"encoding/binary"
	"bytes"
	b64 "encoding/base64"
	"math/rand"
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

	for {
		row, err := csvr.Read()
		if err != nil {
			if err == io.EOF {
				return
			}
			fmt.Println(err)
			return
		}
		var buf bytes.Buffer
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
		sEnc := b64.StdEncoding.EncodeToString(buf.Bytes())

		var buf1 bytes.Buffer
		rssi := int16(rand.Intn(100) * -1)
		err = binary.Write(&buf1, binary.LittleEndian, rssi)
		if err != nil {
			fmt.Println(err)
			return
		}
		sEnc1 := b64.StdEncoding.EncodeToString(buf1.Bytes())
		
		line := []string {"T",sEnc,sEnc1}

		fmt.Println(strings.Join(line[:], ","))
	}
}
