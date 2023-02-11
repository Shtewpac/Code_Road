import importlib
import subprocess

def import_and_install(library_name, alias=None):
    try:
        if alias:
            globals()[alias] = importlib.import_module(library_name)
        else:
            importlib.import_module(library_name)
        print(f'{library_name} is already installed.')
    except ImportError:
        print(f'{library_name} is not installed. Installing...')
        subprocess.run(["pip", "install", library_name], check=True)
        if alias:
            globals()[alias] = importlib.import_module(library_name)
        print(f'{library_name} has been successfully installed!')



# examples:
# import_and_install('speech_recognition', 'sr') #speech_recognition
# import_and_install('pydub')
# import_and_install('ffmpeg')