import numpy as np
import matplotlib.pyplot as plt
import math
from PIL import Image
from pydub import AudioSegment
from scipy import stats

def plot_ondas(samples,sr):

    # Calcular la duración total de la canción en segundos
    duration = len(samples) / sr

    # Crear un arreglo de tiempo para el eje X
    time = np.linspace(0, duration, len(samples))
    #one_seg = sr
    # Graficar los valores de amplitud en función del tiempo
    plt.figure(figsize=(10, 4))
    plt.plot(time, samples, color="blue")
    plt.title("Valores de Amplitud de la Canción MP3")
    plt.xlabel("Tiempo (s)")
    plt.ylabel("Amplitud")
    plt.grid(True)
    plt.show()

def samples_format(y: np.ndarray):
    y_norm = np.interp(y, (y.min(), y.max()), (-1, +1))

    # Convertir las muestras de audio a int16
    samples = (np.iinfo(np.int16).max * y_norm).astype(np.int16)
    return samples


def closest_factors(p):
    k = 0
    while True:
        factor = int(math.sqrt(p + k))
        while (p + k) % factor != 0:
            factor -= 1
        if factor != 1:
            return factor, (p + k) // factor, k
        k += 1

def get_matrix_from_samples(samples,width,height):
    matrix = np.reshape(samples[:(width*height)], (height, width))
    return matrix

def format_values_to_img(matrix):
    matrix=matrix.astype(np.int32)
    max_value = np.max(matrix)
    min_value = np.min(matrix)
    normalized_matrix = (matrix - min_value) / (max_value - min_value) * 255
    # normalized_matrix = normalized_matrix.astype(np.uint8)
    return normalized_matrix


def split_array(array):

    integer_part = np.floor(array).astype(int)
    first_decimals = np.where(
                        np.floor((array - integer_part) * 1000).astype(int) <= 255,
                        np.floor((array - integer_part) * 1000).astype(int),
                        np.floor((array - integer_part) * 100).astype(int)
                    )
    # TODO: FIX DECIMAL ERROR WHEN 123.045012 returns 11 instead of 12 for third matrix
    second_decimals = np.where(
        np.floor((array - integer_part) * 1000).astype(int) <= 255,
        np.where(
            np.floor(((array - integer_part) * 1000 - first_decimals) * 1000).astype(
                int
            )
            <= 255,
            np.floor(((array - integer_part) * 1000 - first_decimals) * 1000).astype(
                int
            ),
            np.floor(((array - integer_part) * 1000 - first_decimals) * 100).astype(
                int
            ),
        ),
        np.where(
            np.floor(((array - integer_part) * 100 - first_decimals) * 1000).astype(int)
            <= 255,
            np.floor(((array - integer_part) * 100 - first_decimals) * 1000).astype(
                int
            ),
            np.floor(((array - integer_part) * 100 - first_decimals) * 100).astype(int),
        )
    )

    return (
        integer_part.astype("uint8"),
        first_decimals.astype(np.uint8),
        second_decimals.astype(np.uint8),
    )

def export_img(rgb_matrix, path):
    # Convertir la matriz a una imagen RGB
    image = Image.fromarray(rgb_matrix, "RGB")

    # Guardar la imagen como un archivo PNG
    image.save(path)

def show_img(rgb_matrix):
    # Mostrar la imagen
    plt.imshow(rgb_matrix)
    plt.axis("off")
    plt.show()

def get_matrix_from_img(path):

    image = Image.open(path)

    matrix_img_rgb = np.array(image)
    return matrix_img_rgb

def validate_matrix(matrix_original,matrix_generated):
    return np.all(matrix_original == matrix_generated)
def decode_rgb_matrix(matrix_img_rgb):
    matrix_img_r = matrix_img_rgb[:, :, 0]
    matrix_img_g = matrix_img_rgb[:, :, 1]
    matrix_img_b = matrix_img_rgb[:, :, 2]
    return matrix_img_r,matrix_img_g,matrix_img_b

def combine_matrix(matrix_img_r,matrix_img_g,matrix_img_b):
    matrix_img_r = matrix_img_r.astype(str)
    matrix_img_g = np.where(
        matrix_img_g < 26,
        np.where(
            matrix_img_g < 10,
            np.char.add("00", matrix_img_g.astype(str)),
            np.char.add("0", matrix_img_g.astype(str)),
        ),
        matrix_img_g.astype(str),
    )
    matrix_img_b = np.where(
        matrix_img_b < 26,
        np.where(
            matrix_img_b < 10,
            np.char.add("00", matrix_img_b.astype(str)),
            np.char.add("0", matrix_img_b.astype(str)),
        ),
        matrix_img_b.astype(str),
    )

    combined_matrix = np.core.defchararray.add(
        matrix_img_r,
        np.core.defchararray.add(".", np.core.defchararray.add(matrix_img_g, matrix_img_b)),
    )
    combined_matrix = combined_matrix.astype(float)
    return combined_matrix
def unnormalize_matrix(combined_matrix,max_value,min_value):
    matrix_unnormalized = (combined_matrix / 255.0) * (max_value - min_value) + min_value
    return matrix_unnormalized
def export_audio(matrix,sr,path):

    samples = (matrix).astype(np.int16)
    samples_bytes = samples.tobytes()
    audio = AudioSegment(
        samples_bytes,
        frame_rate=sr,
        sample_width=samples.dtype.itemsize,
        channels=1,
    )

    audio.export(path, format="wav")


def comprimir_primer_nivel(array_main, array_second, array_third, mode="moda"):
    comprimido = []
    cuenta_array = []
    second_comprimido = []
    third_comprimido = []
    i = 0
    while i < len(array_main):
        cuenta = 1
        valores_siguientes = [(array_second[i], array_third[i])]
        while i + 1 < len(array_main) and array_main[i] == array_main[i + 1]:
            i += 1
            cuenta += 1
            valores_siguientes.append((array_second[i], array_third[i]))
        value_second = 0
        value_third = 0
        if mode == "moda":
            tuplas_concat = [
                int(str(tupla[0]) + str(tupla[1])) for tupla in valores_siguientes
            ]

            moda = stats.mode(tuplas_concat).mode
            value_second = valores_siguientes[tuplas_concat.index(moda)][0]
            value_third = valores_siguientes[tuplas_concat.index(moda)][1]
        second_comprimido.append(value_second)
        third_comprimido.append(value_third)
        comprimido.append(array_main[i])
        cuenta_array.append(cuenta)
        i += 1
    return (
        np.array(comprimido),
        np.array(second_comprimido),
        np.array(third_comprimido),
        np.array(cuenta_array),
    )


def comprimir_simple_optimizado(
    array_main
):
    print("INICIO")
    # Encontrar los índices donde array_main cambia de valor
    cambios = np.where(array_main[:-1] != array_main[1:])[0] + 1
    print("Array de cambios generados")
    # Dividir los arrays en segmentos donde array_main tiene el mismo valor
    segmentos_main = np.split(array_main, cambios)
    print("Generacion de segmentos")
    # Inicializar listas para los resultados
    comprimido = []
    cuenta_array = []
    # Procesar cada segmento
    print(len(segmentos_main))
    for index, (main) in enumerate(
        zip(segmentos_main)
    ):
        comprimido.append(main[0])
        cuenta_array.append(len(main))
        if index == 10000:
            print("10000 primeros elementos")
        if index == 100000:
            print("100000 primeros elementos")
        if index == 1000000:
            print("1000000 primeros elementos")
        if index == 3500000:
            print("3500000 primeros elementos")
        if index == 7000000:
            print("7000000 primeros elementos")
    print(comprimido)
    return (
        np.array(comprimido),
        np.array(cuenta_array),
    )


def comprimir_primer_nivel_optimizado(
    array_main, array_second, array_third, mode="moda"
):
    print("INICIO")
    # Encontrar los índices donde array_main cambia de valor
    cambios = np.where(array_main[:-1] != array_main[1:])[0] + 1
    print("Array de cambios generados")
    # Dividir los arrays en segmentos donde array_main tiene el mismo valor
    segmentos_main = np.split(array_main, cambios)
    segmentos_second = np.split(array_second, cambios)
    segmentos_third = np.split(array_third, cambios)
    print("Generacion de segmentos")
    # Inicializar listas para los resultados
    comprimido = []
    second_comprimido = []
    third_comprimido = []
    cuenta_array = []

    # Procesar cada segmento
    for index, (main, second, third) in enumerate(
        zip(segmentos_main, segmentos_second, segmentos_third)
    ):
        comprimido.append(main[0])
        cuenta_array.append(len(main))
        if index == 10000:
            print("10000 primeros elementos")
        if index == 100000:
            print("100000 primeros elementos")
        if index == 1000000:
            print("1000000 primeros elementos")
        if index == 3500000:
            print("3500000 primeros elementos")
        if mode == "moda":
            tuplas_concat = np.array(
                [int(str(s) + str(t)) for s, t in zip(second, third)]
            )
            moda = stats.mode(tuplas_concat).mode
            indice_moda = np.where(tuplas_concat == moda)[0][0]
            second_comprimido.append(second[indice_moda])
            third_comprimido.append(third[indice_moda])
        else:
            second_comprimido.append(0)
            third_comprimido.append(0)

    return (
        np.array(comprimido),
        np.array(second_comprimido),
        np.array(third_comprimido),
        np.array(cuenta_array),
    )


def descomprimir_primer_nivel(array, second_array, third_array, cuenta):
    descomprimido = []
    second_descomprimido = []
    third_descomprimido = []
    for index, valor in enumerate(array):
        descomprimido.extend([valor] * cuenta[index])
        second_descomprimido.extend([second_array[index]] * cuenta[index])
        third_descomprimido.extend([third_array[index]] * cuenta[index])
    return (
        np.array(descomprimido),
        np.array(second_descomprimido),
        np.array(third_descomprimido),
    )

def plot_histograma(samples,bins=100):
    plt.hist(samples, bins=bins)
    plt.show()
