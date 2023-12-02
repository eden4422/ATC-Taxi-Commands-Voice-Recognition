import queue
import sounddevice as sd
from vosk import Model, KaldiRecognizer
import sys
import json
from time import sleep
import wave


# A class mocking actual functionality of audiolistening, by returning 
def listen_for_audio(plane_id, audiobitQ, audioComIn, audioComOut):
    listening = True
    nameHeard = False
    
    # TODO : Obstantiate 

    while(True):
        
        if nameHeard:
        
            # TODO : Replace sleep function with listening function
            sleep(5)
            # while audioNotQuiet

            # TODO : Replace this line with the audio file parsed from above
            audio = wave.open("testAudio.wav", 'rb')
            
            audiobitQ.put(audio)
            nameHeard = False
        else:

            sleep(5)
            nameHeard = True
            # TODO : listen for name to be called




'''This script processes audio input from the microphone and displays the transcribed text.'''
# get the samplerate - this is needed by the Kaldi recognizer
device_info = sd.query_devices(sd.default.device[0], 'input')
samplerate = int(device_info['default_samplerate'])

# display the default input device
print("===> Initial Default Device Number:{} Description: {}".format(sd.default.device[0], device_info))

# setup queue and callback function
q = queue.Queue()

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
    with sd.RawInputStream(dtype='int16',
                           channels=1,

                           callback=recordCallback):
        while True:
            data = q.get()        
            if recognizer.AcceptWaveform(data):
                recognizerResult = recognizer.Result()
                # convert the recognizerResult string into a dictionary  
                resultDict = json.loads(recognizerResult)
                if resultDict.get("text", "") != "":
                    print(recognizerResult)
                else:
                    print("no input sound")

except KeyboardInterrupt:
    print('===> Finished Recording')
except Exception as e:
    print(str(e))
