# LED remote (practice target) - RF findings and methodology

- Target: no-brand 869 MHz LED light remote (on/off, dim up/down, color-temperature
  cool/warm, 6 numeric scene buttons)
- Purpose: low-risk practice target to validate the capture-and-analysis toolchain
  before tackling the Zehnder RAD E RF radiator protocol
- Status: air interface characterized at frame level; payload appears
  whitened/encrypted per frame; per-button structural fingerprints established;
  replay acceptance untested
- All numbers below come from clean captures taken Nov 9, 2025 (RTL-SDR at
  1 MS/s, 869.47 MHz center, manual gain, peaks at ~12% of full scale).
  Raw I/Q is kept locally per the captures/ policy.

## 1. Capture chain that works (and what did not)

Validated configuration:

- Nooelec NESDR SMArt v5 + URH 2.10.0, native RTL-SDR backend
- 869.47 MHz center, 1 MS/s, 1 MHz bandwidth, manual gain 27 dB, remote ~0.4 m
- URH file format: complex16s (signed 16-bit LE I/Q)

Pitfalls found (these cost real time - do not repeat):

1. **Clipping poisons everything.** Recording at 80-100% of full scale created
   phantom harmonic tones (+354 kHz artifacts), distorted the envelope timing
   and produced nonsense per-button patterns. Keep the strongest peaks below
   ~1/3 of full scale. Adjust distance rather than gain for fine level control;
   the R820T gain ladder is discrete (no supported step between 14.4 and 27 dB).
2. **URH writes zeros for idle samples.** Both native and RTL-TCP backends
   write I=Q=0 between frames. Zero runs are gap filler, never RF silence.
3. **RTL-TCP over Wi-Fi drops samples.** Bursts arrived chopped: ~27 ms received
   + ~23 ms zero-filled repeating every 50 ms, ~46% of the stream missing.
   Use the native backend.
4. **RTL tuner images move with retune.** Spurious mirror peaks sit symmetric
   about the tune center and MOVE when you retune; real transmitters stay at
   fixed absolute frequencies. Always run the retune test before believing a
   peak in the spectrum analyzer.
5. **The band is crowded.** Somfy io gear transmits at 869.325/869.525 MHz,
   right next to this device. Captures stayed inconsistent until sessions were
   isolated: all other RF devices away or battery out, one button per recording.
6. **Correlate before you trust.** The button-correlation test (peak appears
   only while the button is held) is the only attribution test that matters.

## 2. LED remote - measured protocol facts

Radio parameters, consistent across all buttons:

- Continuous frames; no amplitude keying inside a frame (whole frame is one
  carrier-on run)
- Instantaneous frequency span ~300 kHz: p10/p90 = -345/-46 kHz around a
  -104 kHz median (relative to the 869.47 MHz tune); occupied bandwidth
  (5-95% power) ~ -170..+167 kHz; histogram modes spaced ~40 kHz apart
- Instantaneous-frequency autocorrelation decorrelates after ~3-6 us,
  i.e. effective content rate on the order of 150-300 kbaud with noise-like
  statistics (whitened digital payload)
- Carrier density peaks at -85 kHz offset (869.39 MHz on air); this matches
  the 869.39/869.55 double peak seen on the SA - the upper peak is data
  sideband smear (the "bridge" between peaks)

Frame grammar (taps are short presses, holds ~2 s):

| Family | Frames per press | Frame length | Inter-frame period | Total burst |
| --- | --- | --- | --- | --- |
| BTN1-6 (scenes) | 8 | 13.88 ms | 45.2 ms | ~350 ms |
| DIM up/down tap | 1 | 26.69 ms | - | single frame |
| TEMP cool/warm tap | 1 | 26.69 ms | - | single frame |
| ON-OFF | 4 | 26.69 ms | 58.4 ms | ~210 ms |
| DIM hold | 15-16 | 26.69 ms | 49.8 ms | entire hold |
| TEMP hold | 7-8 | 26.69 ms | 99.6 ms | entire hold |

Payload properties:

- **No frame ever repeats.** Successive frames within one button press
  correlate at ~ +0.02 (quantized instantaneous-frequency streams, any shift);
  cross-button correlation equally flat. A fixed-code protocol is ruled out;
  the payload is whitened/encrypted per frame
- The family-level timing grammar above is perfectly stable and fingerprints
  from the RX envelope alone. The six BTN1-6 buttons are structurally
  identical and cannot be told apart without the payload key

## 3. Integration plan

- **Listener:** ESP32 + CC1101 (868 MHz band-matched module) sampling the
  carrier/RSSI envelope at ~1 kHz resolves the frame grammar; family-level
  command detection is trivial and covers most automation needs
- **Transmitter:** forging frames is out (whitened payload). Replay of
  recorded frames is the open experiment - anti-replay enforcement is
  untested. CC1101 async 2-FSK reaches the symbol rates involved.
  nRF905 is NOT suitable (packet radio, fixed framing, max 50 kbps, no raw
  streaming)
- **Guaranteed fallback:** optocoupler across the physical remote button pads

## 4. Lessons specific to the Zehnder RAD E RF work

1. The Zehnder link is bidirectional (radiator sends room temperature/status
   back). Expect two frame types on air - capture a live paired conversation,
   not just remote presses
2. The pairing handshake (docs/pairing.md) is the highest-value capture
   moment: the receiver is in its most permissive state exactly when IDs are
   exchanged
3. One file per button, labeled, with per-press correlation - the discipline
   that finally produced clean results here
4. Expect whitened payloads on the Zehnder too; structural fingerprinting is
   the identification layer that survives encryption
5. Duty cycle: the 868 MHz sub-band allows ~1% - keep all transmissions sparse
   (see README)

## 5. Analysis tooling

tools/analyze_iq.py loads URH complex16s captures, segments bursts above the
zero-fill gaps and prints per-frame timing and modulation statistics. It
produced every number in this document and is directly reusable for the
868.4 MHz Zehnder captures.

## 6. Open questions

- Replay acceptance of the LED receiver: untested (needs TX-capable hardware)
- Whether BTN1-6 payloads differ deterministically per button (crypto-bound;
  cannot be answered from recordings alone)
- An unidentified co-transmitter seen in early sessions (27 ms frames every
  50 ms with dense ~33 us micro-pulse structure) never matched any labeled
  LED button press; most likely another 869 MHz device - re-identify if seen
