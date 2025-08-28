import wave, math, struct
sr, dur, freq = 16000, 1.0, 440.0
n = int(sr*dur)
with wave.open("test.wav","w") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
    for i in range(n):
        val = int(0.2*32767*math.sin(2*math.pi*freq*i/sr))
        w.writeframes(struct.pack('<h', val))
print("Wrote test.wav")
