# python library imports
import multiprocessing
import queue
import time

# local imports
from Model import trans_model
from commands import *

def transcribe_audio(input_audio_queue,text_queue, com_in_queue, com_out_queue, heartBeat):
    
    running = True
    while running:

        if heartBeat == False:
            heartBeat = True


        # If we get audio in the input_audio_queue, process it
        if not input_audio_queue.empty():        
            print("transcribing begin")
            audio_bits = input_audio_queue.get()
            
            model_link_one = "vosk-model-small-en-us-0.15"
            model_link_two = "vosk-model-small-en-us-0.15"
            model_link_three = "vosk-model-small-en-us-0.15"

            # creating queue for output text
            output_text = multiprocessing.Queue()
            error_queue = multiprocessing.Queue()

            # creating three model processes 
            model_process_one = multiprocessing.Process(target=trans_model, args=(audio_bits, model_link_one, output_text, error_queue))
            model_process_two = multiprocessing.Process(target=trans_model, args=(audio_bits, model_link_two, output_text, error_queue))
            model_process_three = multiprocessing.Process(target=trans_model, args=(audio_bits, model_link_three, output_text, error_queue))

            # start all three processes
            model_process_one.start()
            model_process_two.start()
            model_process_three.start()

            print("started processes\n\n\n\n\n\n\n")
            # sleep until all three processes complete
            model_process_one.join()
            model_process_two.join()
            model_process_three.join()
            print("processes ended")
    
            # adding results to list
            results: list = []

            while not output_text.empty():
                results.append(output_text.get())
    
            print(results)
    
            # checking list for if we have sufficient agreement
            tests_pass = False
            test_passed = None

            if len(results) != 3:
                raise ValueError("There must be exactly 3 results for the decision.")

            # Count occurrences of each decision
            decision_counts = {}
            for result in results:
                if result not in decision_counts:
                    decision_counts[result] = 1
                else:
                    decision_counts[result] += 1

            print(decision_counts)

            # Check for at least 2 out of 3 agreement
            for result, count in decision_counts.items():
                if count >= 2:
                    tests_pass = True
                    test_passed = result

            # Putting translated test on textQ
            if tests_pass == True and test_passed != None:
                text_queue.put(test_passed)

        # Checking com_in queue for commands from threadmanager
        elif not com_in_queue.empty():
            input = com_in_queue.get()
            
            if input[0] == KILLSELF:
                running = False

            # Delta one two three this is ground control please head to runway 33 taxi via Delta Bravo Zulu
            # D123 33 D B Z