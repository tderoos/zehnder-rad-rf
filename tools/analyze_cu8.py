#!/usr/bin/env python3
"""Demodulate FSK/GFSK bursts from an rtl_sdr .cu8 capture and print hex per burst.

Usage:
    python3 tools/analyze_cu8.py capture.cu8 [-f FREQ_HZ] [-s SAMPLE_RATE] [--bitrate HZ]

Requires: numpy. Install with: pip install numpy
"""
import argparse
import sys

import numpy as np


def load_cu8(path):
    raw = np.fromfile(path, dtype=np.int8)
    iq = (raw[0::2].astype(np.float32) + 1j * raw[1::2].astype(np.float32)) / 128.0
    return iq


def find_bursts(power, threshold_db=12.0, min_gap=2000, min_len=500):
    thresh = 10 ** (threshold_db / 10.0) * np.median(power)
    above = power > thresh
    bursts = []
    start = None
    gap = 0
    for i, a in enumerate(above):
        if a:
            if start is None:
                start = i
            gap = 0
        elif start is not None:
            gap += 1
            if gap >= min_gap:
                if i - gap - start >= min_len:
                    bursts.append((start, i - gap))
                start = None
                gap = 0
    if start is not None and len(power) - start >= min_len:
        bursts.append((start, len(power)))
    return bursts


def fm_demod(iq):
    phase = np.angle(iq[1:] * np.conj(iq[:-1]))
    return phase


def estimate_bitrate(fm, sample_rate, search=(1000, 200000)):
    best_br, best_score = None, -1
    for br in range(search[0], search[1], 500):
        sps = sample_rate / br
        if sps < 2:
            continue
        n = int(len(fm) / sps)
        if n < 10:
            continue
        bits = (fm[: n * int(sps)] > 0).astype(np.int8)
        transitions = np.abs(np.diff(bits.reshape(n, int(sps)).mean(axis=1)))
        score = transitions.mean()
        if score > best_score:
            best_score, best_br = score, br
    return best_br


def decode_bits(fm, sample_rate, bitrate):
    sps = sample_rate / bitrate
    n = int(len(fm) / sps)
    if n == 0:
        return b""
    samples = fm[: n * int(sps)].reshape(n, int(sps)).mean(axis=1)
    bits = (samples > 0).astype(np.uint8)
    # pack bits MSB first
    out = bytearray()
    for i in range(0, len(bits) - 7, 8):
        b = 0
        for bit in bits[i : i + 8]:
            b = (b << 1) | int(bit)
        out.append(b)
    return bytes(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("-f", "--freq", type=float, default=868400000, help="center freq Hz (info only)")
    ap.add_argument("-s", "--sample-rate", type=float, default=1000000)
    ap.add_argument("--bitrate", type=float, default=None, help="force bitrate Hz instead of estimating")
    ap.add_argument("--threshold-db", type=float, default=12.0)
    args = ap.parse_args()

    iq = load_cu8(args.file)
    power = np.abs(iq) ** 2
    bursts = find_bursts(power, args.threshold_db)
    print(f"# {args.file}: {len(iq)} samples @ {args.sample_rate:.0f} Hz, center {args.freq:.0f} Hz")
    print(f"# found {len(bursts)} burst(s)")
    for idx, (s, e) in enumerate(bursts):
        seg = iq[max(0, s - 100) : e + 100]
        fm = fm_demod(seg)
        br = args.bitrate or estimate_bitrate(fm, args.sample_rate)
        data = decode_bits(fm, args.sample_rate, br)
        dur_ms = (e - s) / args.sample_rate * 1000
        print(f"burst {idx}: samples {s}-{e} ({dur_ms:.1f} ms), est bitrate {br} bps")
        print(f"  hex: {data.hex()}")
        print(f"  ascii: {data!r}")


if __name__ == "__main__":
    sys.exit(main())
