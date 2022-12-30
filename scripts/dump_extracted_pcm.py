import wave
import logging
from e2sysex import *
import e2_formats as fmt

logging.basicConfig(level=logging.DEBUG)

e = E2Sysex()

logging.debug('Getting decompressed PCM from CPU RAM')
pcm_decomp = e.read_cpu_ram(0xc3000000, 0xf9b2ea)

logging.debug('Writing pcm-dump.wav')
with wave.open('e2-synth-pcm.wav', 'wb') as wavfile:
	wavfile.setparams((1, 2, 44100, 0, 'NONE', 'NONE'))
	wavfile.writeframes(pcm_decomp)


