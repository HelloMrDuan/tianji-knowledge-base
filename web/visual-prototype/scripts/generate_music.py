"""Compose our own quiet pentatonic plucked-string loop; no sampled recordings."""
import math
import random
import struct
import subprocess
import tempfile
import wave
from pathlib import Path

RATE = 44100
DURATION = 32
output = [0.0] * (RATE * DURATION)
# Authored pentatonic phrase, with generous space between plucks.
notes = [(0, 196), (3, 293.665), (6, 329.628), (9, 261.626),
         (12, 220), (16, 196), (19, 261.626), (22, 293.665), (26, 220)]
rng = random.Random(20261002)
for onset, frequency in notes:
    start = int(onset * RATE)
    for i in range(min(6 * RATE, len(output) - start)):
        t = i / RATE
        attack = min(1, t / .018)
        fundamental = math.sin(2 * math.pi * frequency * t) * math.exp(-t / 1.45)
        overtone = .24 * math.sin(4 * math.pi * frequency * t) * math.exp(-t / .62)
        texture = .016 * (rng.random() * 2 - 1) * math.exp(-t / .035)
        output[start + i] += .22 * attack * (fundamental + overtone + texture)
target = Path(__file__).resolve().parents[1] / 'public/music/quiet-waters.ogg'
target.parent.mkdir(parents=True, exist_ok=True)
with tempfile.TemporaryDirectory() as scratch:
    wav = Path(scratch) / 'original.wav'
    with wave.open(str(wav), 'wb') as stream:
        stream.setnchannels(1)
        stream.setsampwidth(2)
        stream.setframerate(RATE)
        stream.writeframes(b''.join(struct.pack('<h', int(max(-1, min(1, x)) * 32767)) for x in output))
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', str(wav),
                    '-c:a', 'libvorbis', '-q:a', '3', str(target)], check=True)
print(f'Original music generated: {target.name} ({target.stat().st_size} bytes)')
