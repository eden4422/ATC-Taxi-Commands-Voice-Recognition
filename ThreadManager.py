import multiprocessing
from datetime import datetime
import queue
import json


AUDPROC = "Audio listening process"
AUDTRAN = "Audio " 

# main task that handles
def thread_managing():

    # Initializing pipes, queues, etc
    errorQ = queue.Queue() # error queue, used by all processes for all error handling
    audioQ = queue.Queue() # audio queue, used by thread manager and audio_listening
    textQ = queue.Queue()

    # Starting 
    audio_listening_process = multiprocessing.Process(target=audio_listening, args=(audioQ, errorQ))

    while(True):

        # Wait idly while audioClipQueue is empty (waiting for task 2 to finish)
        while(audioQ.empty):
            pass

        # Pull audioClip from queue 
        audioClipFound = audioQ.get()

        # Start audio transcribing process using audioclip and wait for results
        audio_transcribing_process = multiprocessing.Process(target=audio_transcribing, args=(audioClipFound, textQ, errorQ))
        audio_transcribing_process.start()
        audio_transcribing_process.join()

        # Getting transcribed text from queue

        transcribedText: str = ""

        if textQ.not_empty():
            transcribedText = textQ.get()
        else:
            transcribedText = "ERROR: Text was not transcribed properly. Please refer to error log."

        # Saving converted text to JSON
        saveToJSON(convertToJSON(transcribedText))

def convertToJSON(text_to_convert):
    # return text in converted format (python dicts are already JSON format)
    converted: dict = {}
    return converted

def saveToJSON(json_file):
    # return a success
    return True

def audio_listening(audio_segment_queue, error_queue):
    # will run concurrently unless it is stopped by a error in the error queue
    while(True):
        for i in range(500):
            pass
        
        audio_segment_queue.put("AUDIO BLAH BLAH BLAH")

def audio_transcribing(input_audio,text_queue, error_queue):
    
    # creating queue for output text
    outputTextQ = queue.Queue()
    
    # creating three model processes 
    model_process_One = multiprocessing.Process(target=model_one, args=(input_audio, outputTextQ, error_queue))
    model_process_two = multiprocessing.Process(target=model_two, args=(input_audio, outputTextQ, error_queue))
    model_process_three = multiprocessing.Process(target=model_three, args=(input_audio, outputTextQ, error_queue))

    # start all three processes
    model_process_One.start()
    model_process_One.start()
    model_process_One.start()

    # sleep until all three processes complete
    model_process_One.join()
    model_process_One.join()
    model_process_One.join()

    # adding results to list
    results: list = []

    while(outputTextQ.not_empty()):
        results.append(outputTextQ.get())

    # checking list for if we have sufficient agreement
    testsPass = False
    testPassed = None

    if len(results) != 3:
        raise ValueError("There must be exactly 3 results for the decision.")

    # Count occurrences of each decision
    decision_counts = {}
    for result in results:
        if result not in decision_counts:
            decision_counts[result] = 1
        else:
            decision_counts[result] += 1

    # Check for at least 2 out of 3 agreement
    for result, count in decision_counts.items():
        if count >= 2:
            testsPass = True
            testPassed = result

    # Putting translated test on textQ
    if testsPass == True and testPassed != None:
        text_queue.put(testPassed)


def model_one(input_audio,output_text_queue, error_queue):
    # runs for a finite ammount of time before 
    for i in range(400):
        pass

    output_text_queue.put("outputText")

def model_two(input_audio, output_text_queue, error_queue):
    for i in range(500):
        pass

    output_text_queue.put("outputText")

def model_three(input_audio, output_text_queue, error_queue):
    for i in range(600):
        pass

    output_text_queue.put("outputText")

if __name__ == "main":
    processMain = multiprocessing.Process(target=thread_managing)
    processMain.start()
    processMain.join()


