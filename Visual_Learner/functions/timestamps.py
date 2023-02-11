# import wave
# import json

# from vosk import Model, KaldiRecognizer, SetLogLevel
# import Word as custom_Word

# model_path = "models/vosk-model-en-us-0.21"
# audio_filename = "Visual_Learner/input/Dec_of_Indep_2.wav"

# model = Model(lang="en-us")
# wf = wave.open(audio_filename, "rb")
# rec = KaldiRecognizer(model, wf.getframerate())
# rec.SetWords(True)

# # get the list of JSON dictionaries
# results = []
# # recognize speech using vosk model
# while True:
#     data = wf.readframes(4000)
#     if len(data) == 0:
#         break
#     if rec.AcceptWaveform(data):
#         part_result = json.loads(rec.Result())
#         results.append(part_result)
# part_result = json.loads(rec.FinalResult())
# results.append(part_result)

# # convert list of JSON dictionaries to list of 'Word' objects
# list_of_Words = []
# for sentence in results:
#     if len(sentence) == 1:
#         # sometimes there are bugs in recognition 
#         # and it returns an empty dictionary
#         # {'text': ''}
#         continue
#     for obj in sentence['result']:
#         w = custom_Word.Word(obj)  # create custom Word object
#         list_of_Words.append(w)  # and add it to list

# wf.close()  # close audiofile

# # output to the screen
# for word in list_of_words:
#     print(word.to_string())

#!/usr/bin/env python3

import subprocess
import sys

from vosk import Model, KaldiRecognizer, SetLogLevel

SAMPLE_RATE = 16000

SetLogLevel(-1)

model = Model(lang="en-us")
rec = KaldiRecognizer(model, SAMPLE_RATE)
rec.SetWords(True)

with subprocess.Popen(["ffmpeg", "-loglevel", "quiet", "-i",
                            sys.argv[1],
                            "-ar", str(SAMPLE_RATE) , "-ac", "1", "-f", "s16le", "-"],
                            stdout=subprocess.PIPE).stdout as stream:

    print(rec.SrtResult(stream))
