"""Procedural sound bed, Python standard library only (wave, math, struct, random).
A soft pad (A minor chord, slow swell), a gentle pulse (low soft thump, 80 per minute) and a soft
tick at each section change. No samples, no downloads. Writes audio/bed.wav (44.1 kHz, mono, 16 bit)."""
import json, math, pathlib, random, struct, wave
root = pathlib.Path(__file__).resolve().parent.parent
random.seed(7)
SR = 44100
d = json.load(open(root / "durations.json"))
total = d["total_seconds"] + 0.5
N = int(total * SR)
buf = [0.0] * N
# pad: four sines with a pair of slightly detuned voices, slow amplitude swell
for f, a in ((110.0, 0.30), (164.81, 0.22), (220.0, 0.22), (261.63, 0.16), (329.63, 0.08)):
    for det, ph in ((0.0, 0.0), (0.35, 1.3)):
        w = 2 * math.pi * (f + det) / SR
        lfo = 2 * math.pi * (0.05 + 0.01 * (f % 7)) / SR
        for i in range(N):
            buf[i] += a * 0.5 * math.sin(w * i + ph) * (0.75 + 0.25 * math.sin(lfo * i + ph))
# pulse: soft thump, 55 Hz sine with short decay, every 0.75 s
beat = int(0.75 * SR)
for k in range(0, N, beat):
    for j in range(int(0.35 * SR)):
        if k + j >= N:
            break
        t = j / SR
        buf[k + j] += 0.55 * math.sin(2 * math.pi * (55 + 25 * math.exp(-t * 30)) * t) * math.exp(-t * 9)
# ticks at section boundaries: 40 ms soft blip at 1760 Hz
t0 = 0.0
marks = []
for s in sorted(d["sections"], key=int):
    marks.append(t0)
    t0 += d["sections"][s]["frames"] / 30
for m in marks:
    k = int(m * SR)
    for j in range(int(0.12 * SR)):
        if k + j >= N:
            break
        t = j / SR
        buf[k + j] += 0.5 * math.sin(2 * math.pi * 1760 * t) * math.exp(-t * 38)
# fade in and out, normalize to a peak of 0.5 (the mix lowers it further under the voice)
peak = max(abs(x) for x in buf)
fade = int(1.5 * SR)
out = bytearray()
for i, x in enumerate(buf):
    g = min(1.0, i / fade, (N - i) / fade)
    out += struct.pack("<h", int(max(-1, min(1, x / peak * 0.5 * g)) * 32767))
with wave.open(str(root / "audio" / "bed.wav"), "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(bytes(out))
print("bed written", round(total, 2), "s; section ticks at", [round(m, 2) for m in marks])
