# python library imports
import multiprocessing
import threading
from datetime import datetime
import queue
import json
import wave

# local imports
from JsonSaving import *
from CommandTranscription import *
from AudioListening import *
from CommandTranscription import *
from QueueKeys import *
from Frontend import *


# main task that handles
def thread_managing():
    
    # Temp variable for airplane identifier
    plane_ids = ["delta one two three", "united six seven eight"]

    # Initializing pipes, queues, etc
    frontComIn = multiprocessing.Queue() # frontend queue, used by thread manager -> frontend
    frontComOut = multiprocessing.Queue() 


    audiobitQ = multiprocessing.Queue() # audio queue, used by audio_listening -> thread_manager
    
    audioComIn = multiprocessing.Queue() # audio comm in
    audioComOut = multiprocessing.Queue() # audio comm out
    
    textQ = multiprocessing.Queue() # 
    
    transComIn = multiprocessing.Queue()
    transComOut = multiprocessing.Queue()

    # Starting frontend process
    print("starting frontend process")
    #frontend_process = multiprocessing.Process(target=front_window, args=(frontComIn, frontComOut))
    #frontend_process.start()

    # Starting audio listening process
    print("starting audio process")
    audio_listening_process = multiprocessing.Process(target=listen_for_audio, args=(plane_ids, audiobitQ, audioComIn, audioComOut))
    audio_listening_process.start()

    running = True

    while(running):

        # Wait idly while audioClipQueue is empty (waiting for task 2 to finish)
        
        print("waiting for audio in audio queue")
        while(audiobitQ.empty() and audioComOut.empty()):
            pass#print(audiobitQ.queue)
        
        # Pull audioClip from queue 
        audioClipFound = audiobitQ.get()

        # Start audio transcribing process using audioclip and wait for results
        
        audio_transcribing_process = multiprocessing.Process(target=transcribe_audio, args=(audioClipFound, textQ, transComIn, transComOut))
        audio_transcribing_process.start()
        audio_transcribing_process.join()
        print("transcriber process finished")

        transcribedText = textQ.get()

        print("transcribedtext:")
        print(transcribedText)


        save_to_json(convert_to_json(transcribedText))
        print(43)
        
        



if __name__ == "__main__":

    print("starting thread manager")
    processMain = multiprocessing.Process(target=thread_managing)
    processMain.start()
    processMain.join()
    print("threadmanager finished")







