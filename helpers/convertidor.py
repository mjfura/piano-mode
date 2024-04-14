from pydub import AudioSegment
import os
from helpers.mp3_midi import mp3_to_piano
# Paso 1: Convertir el archivo MP3 a un objeto AudioSegment
mp3_file = "audio_muestra.mp3"
audio = AudioSegment.from_mp3(mp3_file)

# Paso 2: Guardar el objeto AudioSegment como un archivo WAV temporal
wav_file = "cancion_temporal.wav"
audio.export(wav_file, format="wav")

# Paso 3: Convertir el archivo WAV a MIDI utilizando una herramienta externa
mp3_to_piano(mp3_file, "cancion_temporal.mid")
#os.system(f"sonic-annotator -d vamp:qm-vamp-plugins:qm-keydetector:note -w midi {wav_file}")

# Paso 4: Convertir el archivo MIDI a MP3 utilizando FluidSynth
midi_file = "cancion_temporal.mid"
mp3_output_file = "audio_muestra_final.mp3"

# Ejecutar FluidSynth para convertir el archivo MIDI a audio MP3
os.system(f"fluidsynth -ni sound_font.sf2 {midi_file} -F {mp3_output_file}")

# Paso 5: Eliminar los archivos temporales
os.remove(wav_file)
os.remove(midi_file)

print("¡La conversión ha sido completada!")