import queue

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