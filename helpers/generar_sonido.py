from pydub import AudioSegment
import numpy as np
notas={
"C": 261.63,
"D": 293.66,
"E": 329.63,
"F": 349.23,
"G": 392.00,
"A": 440.00,
"B": 493.88,
'T':0.00
}
notas_cancion=np.array([
    'C','C','D','C','F','E','T','C','C','D','C','G','F'
])
#2seg para el T
#C C D C F E   C C D C G F
#C C D C F E   C C D C G F
#C C C' A F E D   A A G F D E
#D D C C G F E C C D C G F
def generate_audio(duration=13, frequency=440, volume=50):
    # Crear un array de numpy con los valores de la onda sinusoidal
    muestreo=44100
    numeros_duracion=np.arange(muestreo*duration)
    samples=[]
    for num in numeros_duracion:
        if num%muestreo==0:
            frequency=notas[notas_cancion[num//muestreo]]
        value=np.sin(2 * np.pi * frequency * num/ muestreo)
        samples.append(value)
    samples=np.array(samples).astype(np.float32)
    samples /= np.max(np.abs(samples))

    print('Samples ',samples, samples.shape, samples.size)
    # Escalar los valores para ajustar el volumen
    scaled_samples = (samples * (10 ** (volume / 20))).astype(np.float32)
    print('Scaled samples ',scaled_samples ,scaled_samples.shape, scaled_samples.size)
    # Crear un objeto AudioSegment a partir de los datos de audio
    audio = AudioSegment(
        scaled_samples.tobytes(),
        frame_rate=muestreo,
        sample_width=scaled_samples.dtype.itemsize,
        channels=1
    )

    return audio

# Generar audio de 5 segundos con una frecuencia de 440 Hz y guardar como archivo MP3
audio = generate_audio(duration=len(notas_cancion))
audio.export("output.mp3", format="mp3")

print("¡Archivo de audio generado correctamente!")