# Firmware

- `sniffer/` - ESP32 + CC1101 (or nRF905) sketch that logs
  `[freq, rssi, hex payload]` per received frame to serial/MQTT.
- `bridge/` - ESPHome external component that decodes radiator frames and
  transmits remote commands, exposing `climate` + `sensor` entities to
  Home Assistant via the native API.

Pinout (CC1101): SCK/GD0/MISO/MOSI/CS/GDO2 to ESP32 GPIOs, VCC 3.3V (never 5V).
