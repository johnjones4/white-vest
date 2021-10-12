#include <SPI.h>
#include <RH_RF95.h>
#include <base64.hpp>

#define RF95_FREQ 915.0

#define RF95_INT     3
#define RF95_CS      4
#define RF95_RST     2

RH_RF95 rf95(RF95_CS, RF95_INT);

void setup() {
  Serial.begin(9600);
  while (!Serial);
  if (!rf95.init()) {
    Serial.println("init failed");
  }
  if (!rf95.setFrequency(RF95_FREQ)) {
    Serial.println("Set freq failed");
  }
  rf95.setModeRx();
  Serial.println("Ready!");
}

void loop() {
  uint8_t buf[RH_RF95_MAX_MESSAGE_LEN];
  uint8_t len = sizeof(buf);
  if (rf95.recv(buf, &len)) {
    
    unsigned char data_base64[255];
    encode_base64((char*)buf, len, data_base64);
    
    int16_t rssi = rf95.lastRssi();
    unsigned char rssi_base64[255];
    uint8_t rssi_low = rssi & 0xff;
    uint8_t rssi_high = (rssi >> 8);
    uint8_t rssi_array[2] = {rssi_low, rssi_high};
    encode_base64((char*)rssi_array, 2, rssi_base64);
    
    Serial.print("T,");
    Serial.print((char *) data_base64);
    Serial.print(",");
    Serial.print((char *) rssi_base64);
    Serial.print("\n");
  } else {
    delay(100);
  }
}
