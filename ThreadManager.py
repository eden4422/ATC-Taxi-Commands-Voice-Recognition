# python library imports
import multiprocessing
import threading
from datetime import datetime
import queue
import json
import wave
import Text_To_JSON
import Mongo_Read_Data

# local imports
from CommandTranscription import *
from AudioListening import *
from CommandTranscription import *

from myGUI import *
from commands import *

import time

# main task that handles
def thread_managing():
    
    # Airplane identifier
    plane_id = "delta one two three"

    try:
        with open('settings.json', 'r') as json_file:
            settings_data = json.load(json_file)
            plane_id = settings_data['plane_id']
            return plane_id
    except FileNotFoundError:
        print("settings.json not found. Make sure the file exists.")
        return None
    except KeyError:
        print("Error: 'plane_id' key not found in settings.json.")
        return None
    plane_ids = ["delta one two three", "united six seven eight", "delta five eight nine two"]

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

    # Creating frontend process
    frontend_process = multiprocessing.Process(target=getGoing, args=(frontComIn, frontComOut))
    
    print("Starting frontend process")
    frontend_process.start()

    # Creating audio listening process
    audio_listening_process = multiprocessing.Process(target=listen_for_audio, args=(plane_ids, listenAudioOutQ, listenComIn, listenComOut))
    
    # Creating audio transcribing process
    audio_transcribing_process = multiprocessing.Process(target=transcribe_audio, args=(transAudioInQ, transTextOutQ, transComIn, transComOut))
    
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
            phoentetic_text = Text_To_JSON.phonetic_command_translator(transcribedText)
            parsed_text = Text_To_JSON.parse_taxi_command(phoentetic_text)
            Text_To_JSON.save_to_JSON(parsed_text)
            JSON_to_Mongo.Write_to_Mongo()
            print("Transcribed Text: "+transcribedText )
            frontComIn.put((updateCommandBox,transcribedText))



        # If message recieved from frontend
        elif not frontComOut.empty():
            output = frontComOut.get()
            
            if output[0] == KILLCHILDREN:
                frontend_process.kill()
                
                listenComIn.put((KILLSELF,"kill self"))
                transComIn.put((KILLSELF,"kill self"))

                time.sleep(2)

                audio_listening_process.kill()
                audio_transcribing_process.kill()


                print("Awaiting threads to kill selves")

                running = False

            elif output[0] == MUTE:
                print("toggle mute")
                listenComIn.put((MUTE,"toggle mute"))

            elif output[0] == START:
                print("Starting audio listening process")
                audio_listening_process = multiprocessing.Process(target=listen_for_audio, args=(plane_ids, listenAudioOutQ, listenComIn, listenComOut))
                audio_listening_process.start()

                print("Starting audio transcribing process")
                audio_transcribing_process = multiprocessing.Process(target=transcribe_audio, args=(transAudioInQ, transTextOutQ, transComIn, transComOut))
                audio_transcribing_process.start()
            
            elif output[0] == STOP:
                print("Stopping listening, going on standby")

                listenComIn.put((KILLSELF,"kill self"))
                transComIn.put((KILLSELF,"kill self"))
            


        # If message recieved from listener
        elif not listenComOut.empty():
            output = listenComOut.get()
                
            if output[0] == "allAudio":
                frontComIn.put((updateAllSpeechBox,output[1]))
                print(output)
            
        # If message recieved from transcriber
        elif not transComOut.empty():
            pass
        
        

if __name__ == "__main__":



    print("starting thread manager")
    processMain = multiprocessing.Process(target=thread_managing)
    processMain.start()
    processMain.join()
    print("threadmanager finished")