import queue
import sounddevice as sd
from vosk import Model, KaldiRecognizer
import sys
import json
from time import sleep
import wave
import multiprocessing
import queue
import io


# A class mocking actual functionality of audiolistening, by returning 
def listen_for_audio(plane_id, audiobitQ, audioComIn, audioComOut):
    print("started listening")
    '''This script processes audio input from the microphone and displays the transcribed text.'''
    # get the samplerate - this is needed by the Kaldi recognizer
    device_info = sd.query_devices(sd.default.device[0], 'input')
    samplerate = int(device_info['default_samplerate'])

    # display the default input device
    print("===> Initial Default Device Number:{} Description: {}".format(sd.default.device[0], device_info),flush=True)

    # setup queue and callback function
    q = multiprocessing.Queue()

    def recordCallback(indata, frames, time, status):
        if status:
            print(status, file=sys.stderr)
        q.put(bytes(indata))
    
    # build the model and recognizer objects.
    print("===> Build the model and recognizer objects.  This will take a few minutes.")
    model = Model("vosk-model-small-en-us-0.15")
    recognizer = KaldiRecognizer(model, samplerate)
    recognizer.SetWords(False)

    print("===> Begin recording. Press Ctrl+C to stop the recording ")


    try:
        with sd.RawInputStream(dtype='int16', channels=1, callback=recordCallback):
            while True:
                audio_data = q.get()        
                if recognizer.AcceptWaveform(audio_data):
                    recognizerResult = recognizer.Result()
                    # convert the recognizerResult string into a dictionary  
                    resultDict = json.loads(recognizerResult)
                    resultText: str = resultDict["text"]
                    if plane_id in resultText:
                        print(recognizerResult)

                        audiobitQ.put((audio_data, samplerate))
                        print(audiobitQ)
                    else:
                        print("no input sound")

    except KeyboardInterrupt:
        print('===> Finished Recording')
    except Exception as e:
        print(str(e))



def save_as_wav(audio_data, samplerate):
    wav_buffer = io.BytesIO()

    with wave.open(wav_buffer, 'wb') as wave_file:
        wave_file.setnchannels(1)  # Mono
        wave_file.setsampwidth(2)  # 2 bytes per sample
        wave_file.setframerate(samplerate)
        wave_file.writeframes(audio_data)

    return wav_buffer.getvalue()
