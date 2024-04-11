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
def listen_for_audio(flight_IDs, audiobitQ, audio_com_in, audio_com_out, heartBeat):
    
    if heartBeat == False:
        heartBeat = True

    muted = True

    file_number = 0
    # get the samplerate - this is needed by the Kaldi recognizer
    device_info = sd.query_devices(sd.default.device[0], 'input')
    samplerate = int(device_info['default_samplerate'])

    # display the default input device
    print("===> Initial Default Device Number:{} Description: {}".format(sd.default.device[0], device_info))

    # setup queue and callback function
    q = queue.Queue()

    def recordCallback(in_data, frames, time, status):
      
        if muted != True:
            if status:
                print(status, file=sys.stderr)
            q.put(bytes(in_data))

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
                #print("listening")
                #print(muted)
                #print(heartBeat)
                if heartBeat == False:
                    heartBeat = True

                if not audio_com_in.empty():
                    
                    input = audio_com_in.get()
                    if input[0] == MUTE:
                        muted = not muted

                if not q.empty():   
                     
                    data = q.get()
                    #print(data) 
                    recording_data += data  # Accumulate audio data
                    if recognizer.AcceptWaveform(data):
                        recognizer_result = recognizer.Result()
                        # convert the recognizerResult string into a dictionary
                        result_dict = json.loads(recognizer_result)

                        # added array of touples that 
                        for words in result_dict["result"]:
                            confidence_touples = (words["conf"],words["word"])
                            print(confidence_touples)
                            

                        result_text: str = result_dict["text"]
                        print(result_text)
                        audio_com_out.put(("allAudio", result_text))

                        if any(ID in result_text for ID in flight_IDs):

                            # Save the accumulated audio data to a WAV file
                            with wave.open(f'output{file_number}.wav', 'w') as wf:
                                wf.setnchannels(1)
                                wf.setsampwidth(2)
                                wf.setframerate(samplerate)
                                wf.writeframes(recording_data[-frame_limit:])
                                file_number += 1
                                if file_number == 100:
                                    file_number = 0
                                    
                            audiobitQ.put((recording_data,samplerate))

                            recording_data = b''  # Reset accumulated audio data

                        else:
                            recording_data = b''
                            print("no flight ID found")

    except KeyboardInterrupt:
        print('===> Finished Recording')
    except Exception as e:
        print(str(e))