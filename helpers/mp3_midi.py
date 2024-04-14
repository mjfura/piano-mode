import librosa
import numpy as np
from midiutil import MIDIFile

def mp3_to_piano(mp3_file, output_midi_file):
    # Cargar el archivo MP3
    y, sr = librosa.load(mp3_file)

    # Extraer características de frecuencia de Mel (MFCC)
    mfccs = librosa.feature.mfcc(y=y, sr=sr)

    # Convertir las características MFCC a un espectrograma
    spectrogram = np.abs(librosa.stft(y))

    # Identificar picos en el espectrograma para detectar notas
    notes = []
    for col in mfccs.T:
        picked_note = librosa.util.peak_pick(col, pre_max=5, post_max=5, pre_avg=5, post_avg=5, delta=0, wait=0)
        if picked_note.size > 0:
            notes.append(picked_note[0])

    # Crear un archivo MIDI
    midi = MIDIFile(1)  # Solo una pista en el archivo MIDI
    time = 0
    tempo = 60  # Tempo en BPM (puedes ajustar esto según sea necesario)

    # Agregar notas al archivo MIDI
    for note in notes:
        midi.addNote(0, 0, int(note), time, 1, 100)  # Agregar nota al canal 0
        time += 1

    # Escribir el archivo MIDI
    with open(output_midi_file, "wb") as f:
        midi.writeFile(f)