import queue
import sounddevice as sd
from vosk import Model, KaldiRecognizer
import sys
import json
from time import sleep
import wave
import multiprocessing
import queue
from commands import *


# A class mocking actual functionality of audiolistening, by returning 
def listen_for_audio(flight_IDs, audiobitQ, audioComIn, audioComOut, heartBeat):
    
    muted = True

    fileNum = 0
    # get the samplerate - this is needed by the Kaldi recognizer
    device_info = sd.query_devices(sd.default.device[0], 'input')
    samplerate = int(device_info['default_samplerate'])

    # display the default input device
    print("===> Initial Default Device Number:{} Description: {}".format(sd.default.device[0], device_info))

    # setup queue and callback function
    q = queue.Queue()

    def recordCallback(indata, frames, time, status):
      
        if not muted:
            if status:
                print(status, file=sys.stderr)
            q.put(bytes(indata))

    # build the model and recognizer objects.
    print("===> Build the model and recognizer objects.  This will take a few minutes.")
    model = Model("vosk-model-small-en-us-0.15")
    recognizer = KaldiRecognizer(model, samplerate)
    recognizer.SetWords(True)

    desired_duration = 40  #10 = 5 seconds
    frame_limit = int(samplerate * desired_duration)


    print("===> Begin recording. Press Ctrl+C to stop the recording ")
    try:
        recording_data = b''  # Accumulate audio data

        with sd.RawInputStream(dtype='int16',
                            channels=1,
                            callback=recordCallback):
            while True:
              
                if not audioComIn.empty():
                    input = audioComIn.get()
                    if input[0] == MUTE:
                        muted = not muted
                if not q.empty():     
                    data = q.get()
                    recording_data += data  # Accumulate audio data
                    if recognizer.AcceptWaveform(data):
                        recognizerResult = recognizer.Result()
                        # convert the recognizerResult string into a dictionary
                        resultDict = json.loads(recognizerResult)
                        resultText: str = resultDict["text"]
                        print(resultText)
                        audioComOut.put(("allAudio", resultText))

                        if any(ID in resultText for ID in flight_IDs):

                            # Save the accumulated audio data to a WAV file
                            with wave.open(f'output{fileNum}.wav', 'w') as wf:
                                wf.setnchannels(1)
                                wf.setsampwidth(2)
                                wf.setframerate(samplerate)
                                wf.writeframes(recording_data[-frame_limit:])
                                fileNum += 1
                                if fileNum == 100:
                                    fileNum = 0
                                    
                            audiobitQ.put((recording_data,samplerate))

                            recording_data = b''  # Reset accumulated audio data

                        else:
                            recording_data = b''
                            print("no input sound")

    except KeyboardInterrupt:
        print('===> Finished Recording')
    except Exception as e:
        print(str(e))