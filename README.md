# Zehnder RAD E RF (Metropolitan) 868 MHz protocol

Reverse engineering of the proprietary 868 MHz RF protocol used between the
Zehnder "Afstandsbediening RF" remote (part 887280) and Zehnder electric
design radiators with the "RAD E RF" control platform, including the
Zehnder Metropolitan Elektrisch (MET). Goal: a local Home Assistant bridge
(ESP32 + CC1101/nRF905) exposing climate control and room temperature.

## Status

- [x] Manual analyzed (`RAD RF Bedienung` verkorte handleiding, V01-2023 / 972000321)
- [x] RF capture methodology validated on a practice target (869 MHz LED remote, see docs/led-remote-findings.md)
- [ ] RF captures taken
- [ ] Frame structure decoded
- [ ] Pairing handshake documented
- [ ] ESP32 bridge firmware
- [ ] Home Assistant integration

## Known facts (from the manual)

- Remote: Zehnder Afstandsbediening RF, 868 MHz, bidirectional, up to 16 devices
- Radiator holds the room temperature sensor and open-window detection; the
  remote only sends setpoint/mode/program/boost commands and displays the
  temperature received back from the radiator
- Modes: frost protection (fixed 7 C), eco/night (day temp -3.5 C, min 7 C),
  comfort/day (7-28 C), weekly programs P1/P2, boost (default 60 min)
- Pairing: 2x short press on radiator LED (purple blinking, 1 min window),
  then hold `+` on remote for 5 s (`RF 0` -> `RF 1`)
- Pilot-wire input (`3 Pi`) exists in hardware but is disabled on NL-market units

## Repo layout

- `captures/` - raw I/Q or hex dumps per button press
- `docs/protocol.md` - decoded frame layout
- `docs/pairing.md` - pairing handshake
- `docs/led-remote-findings.md` - practice-target (869 MHz LED remote) RF findings and capture methodology
- `firmware/` - ESP32 + CC1101/nRF905 sniffer/transmitter and ESPHome bridge
- `tools/` - capture analysis helpers (`analyze_iq.py`)

## Hardware used

- Nooelec RTL-SDR v5 (recon/sniffing)
- ESP32 + CC1101 868 MHz (sniff + transmit bridge), nRF905 as alternative
  (Zehnder ventilation RF gear is confirmed nRF905, channel 118 = 868.4 MHz)

## Safety / legal

Work only on your own devices. 868 MHz sub-band duty cycle is ~1% (~36 s/hour)
- keep transmissions sparse. Never connect the pilot wire to earth.

## References

- [eelcohn/ZehnderComfoair](https://github.com/eelcohn/ZehnderComfoair) - Zehnder ventilation RF (nRF905) reverse engineering
- [Sanderhuisman/ESPHome-Zehnder-RF](https://github.com/Sanderhuisman/ESPHome-Zehnder-RF) - ESPHome bridge for ComfoAir RF
