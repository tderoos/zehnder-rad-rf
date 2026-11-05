# Zehnder RAD E RF - protocol notes

Work in progress. Fill in from `captures/`.

## Radio parameters (to confirm)

- Frequency: expect 868.3-868.5 MHz; Zehnder ventilation RF uses channel 118 = 868.4 MHz (nRF905)
- Modulation: likely GFSK/FSK (to confirm from I/Q captures)
- Bitrate / deviation: TBD

## Frame layout (hypothesis)

| Field | Size | Notes |
| --- | --- | --- |
| Preamble | ? | |
| Device/network ID | ? | learned during pairing |
| Command | ? | mode / setpoint / boost / power |
| Payload | ? | e.g. setpoint in 0.5 C steps |
| Checksum/CRC | ? | |

## Command map (to fill in)

| Button | Frame (hex) | Notes |
| --- | --- | --- |
| mode | | |
| + | | |
| - | | |
| boost | | |
| power | | |

## Radiator -> remote frames

Room temperature is transmitted back (remote displays it); open-window and
mode status are reflected on the remote display.
