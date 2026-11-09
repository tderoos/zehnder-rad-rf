#!/usr/bin/env python3
"""Analyze URH complex16s (signed 16-bit LE) I/Q captures:
find RF bursts above the zero-fill idle gaps, print frame timing
and modulation statistics per burst.

Used for the LED practice remote (docs/led-remote-findings.md);
directly reusable for Zehnder RAD E RF captures (868.4 MHz).

Example:
    python3 tools/analyze_iq.py capture.complex16s --fs 1000000
"""
import argparse
import numpy as np


def load_iq(path):
    raw = np.fromfile(path, dtype="<i2")
    if raw.size % 2:
        raw = raw[:-1]
    return raw[0::2].astype(np.float64) + 1j * raw[1::2].astype(np.float64)


def bursts(mag, fs, min_ms):
    """Segments of nonzero samples (URH zero-fills idle time) >= min_ms."""
    on = mag > 10
    runs, i, n = [], 0, len(on)
    while i < n:
        if on[i]:
            j = i
            while j < n and on[j]:
                j += 1
            runs.append((i, j))
            i = j
        else:
            i += 1
    return [(s, e) for s, e in runs if (e - s) / fs * 1000 >= min_ms]


def frame_stats(z, s, e, fs):
    seg = z[s:e]
    ph = np.unwrap(np.angle(seg))
    freq = np.diff(ph) * fs / (2 * np.pi)
    p10, med, p90 = np.percentile(freq, [10, 50, 90])
    L = len(seg)
    S = np.abs(np.fft.fftshift(np.fft.fft(seg * np.hanning(L)))) ** 2
    fr = np.fft.fftshift(np.fft.fftfreq(L, 1 / fs))
    c = np.cumsum(S) / S.sum()
    f05 = fr[min(len(fr) - 1, np.searchsorted(c, 0.05))]
    f95 = fr[min(len(fr) - 1, np.searchsorted(c, 0.95))]
    return med, p10, p90, f05, f95


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("capture", help="path to .complex16s file")
    ap.add_argument("--fs", type=float, default=1e6, help="sample rate (Hz)")
    ap.add_argument("--min-burst-ms", type=float, default=3.0,
                    help="minimum burst length to report (ms)")
    args = ap.parse_args()

    z = load_iq(args.capture)
    mag = np.abs(z)
    bb = bursts(mag, args.fs, args.min_burst_ms)
    print(f"{args.capture}: {len(z) / args.fs:.2f} s, {len(bb)} burst(s)")
    for k, (s, e) in enumerate(bb[:16]):
        med, p10, p90, f05, f95 = frame_stats(z, s, e, args.fs)
        gap = (s - bb[k - 1][1]) / args.fs * 1000 if k else 0.0
        print(f"  #{k + 1:2d} @{s / args.fs * 1000:8.1f} ms  "
              f"len {(e - s) / args.fs * 1000:6.2f} ms  prev-gap {gap:6.2f} ms")
        print(f"       inst-freq med {med / 1e3:+6.0f} kHz "
              f"(p10/90 {p10 / 1e3:+.0f}/{p90 / 1e3:+.0f})  "
              f"occupied {f05 / 1e3:+.0f}..{f95 / 1e3:+.0f} kHz")


if __name__ == "__main__":
    main()
