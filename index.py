from pynput import keyboard
import helpers.generar_sonido
def on_press(key):
    try:
        print(f'Tecla presionada {key.char}')
    except AttributeError:
        print(f'Ha ocurrido un error con {key}')

def on_release(key):
    print(f' Tecla soltada {key}')
    if key == keyboard.Key.esc:
        # Stop listener
        return False

# Collect events until released
#with keyboard.Listener(
#        on_press=on_press,
#        on_release=on_release) as listener:
#    listener.join()
