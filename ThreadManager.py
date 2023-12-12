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
from myGUI import *
from commands import *

# main task that handles
def thread_managing():
    
    # Temp variable for airplane identifier
    plane_ids = ["delta one two three", "united six seven eight"]

    # Initializing pipes, queues, etc
    frontComIn = multiprocessing.Queue() # frontend queue, used by thread manager -> frontend
    frontComOut = multiprocessing.Queue() 

    listenAudioOutQ = multiprocessing.Queue() # audio queue, used by audio_listening -> thread_manager
    
    listenComIn = multiprocessing.Queue() # audio comm in
    listenComOut = multiprocessing.Queue() # audio comm out
    
    transAudioInQ = multiprocessing.Queue()
    transTextOutQ = multiprocessing.Queue() # 

    transComIn = multiprocessing.Queue()
    transComOut = multiprocessing.Queue()

    # Starting frontend process
    print("starting frontend process")
    frontend_process = multiprocessing.Process(target=getGoing, args=(frontComIn, frontComOut))
    frontend_process.start()

    # Starting audio listening process
    print("starting audio process")
    audio_listening_process = multiprocessing.Process(target=listen_for_audio, args=(plane_ids, listenAudioOutQ, listenComIn, listenComOut))
    audio_listening_process.start()

    # Starting audio transcribing process
    print("starting audio transcribing process")
    audio_transcribing_process = multiprocessing.Process(target=transcribe_audio, args=(transAudioInQ, transTextOutQ, transComIn, transComOut))
    audio_transcribing_process.start()

    running = True

    while(running):

        # If audio bit was recorded
        if not listenAudioOutQ.empty():
            
            # Pull audioClip from queue and add to transQ
            audioClipFound = listenAudioOutQ.get()
            transAudioInQ.put(audioClipFound)
            
        # If text was successfully transcribed
        elif not transTextOutQ.empty():

            transcribedText = transTextOutQ.get()
            frontComIn.put((updateCommandBox,transcribedText))

            # TODO : JSON SAVING

        # If message recieved from frontend
        elif not frontComOut.empty():
            output = frontComOut.get()
            
            if output[0] == KILLCHILDREN:
                frontComIn.put((KILLSELF,"kill self"))
                listenComIn.put((KILLSELF,"kill self"))
                transComIn.put((KILLSELF,"kill self"))

                print("Awaiting threads to kill selves")

                frontend_process.join()
                audio_listening_process.join()
                audio_transcribing_process.join()

                running = False

            elif output[0] == MUTE:
                listenComIn.put(MUTE,"toggle mute")

            elif output[0] == START:
                audio_listening_process.start()
                audio_transcribing_process.start()

        # If message recieved from listener
        elif not listenComOut.empty():
            output = listenComOut.get()
                
            if output[0] == "allAudio":
                frontComIn.put((updateAllSpeechBox,output[1]))
                print(output)
            
        # If message recieved from transcriber
        elif not transComOut.empty():
            pass
        

        print("waiting for audio in audio queue")

        while(True):
            if not listenAudioOutQ.empty():
                break
            elif not listenComOut.empty():
                output = listenComOut.get()
                
                if output[0] == "allAudio":
                    frontComIn.put((updateAllSpeechBox,output[1]))
                    print(output)
            


        # Pull audioClip from queue 
        audioClipFound = listenAudioOutQ.get()

        # Start audio transcribing process using audioclip and wait for results
        
        audio_transcribing_process = multiprocessing.Process(target=transcribe_audio, args=(audioClipFound, transTextOutQ, transComIn, transComOut))
        audio_transcribing_process.start()
        audio_transcribing_process.join()
        print("transcriber process finished")

        transcribedText = transTextOutQ.get()

        print("transcribedtext:")
        print(transcribedText)


        save_to_json(convert_to_json(transcribedText))
        
        

if __name__ == "__main__":

    print("starting thread manager")
    processMain = multiprocessing.Process(target=thread_managing)
    processMain.start()
    processMain.join()
    print("threadmanager finished")