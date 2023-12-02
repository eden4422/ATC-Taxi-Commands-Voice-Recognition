# python library imports
import multiprocessing
import queue

# local imports
from Model import trans_model


def transcribe_audio(input_audio,text_queue, com_in_queue,com_out_queue):
    print("transcribing begin")
    model_link_one = "vosk-model-small-en-us-0.15"
    model_link_two = "vosk-model-small-en-us-0.15"
    model_link_three = "vosk-model-small-en-us-0.15"

    # creating queue for output text
    outputTextQ = multiprocessing.Queue()
    error_queue = multiprocessing.Queue()



    # creating three model processes 
    model_process_one = multiprocessing.Process(target=trans_model, args=(input_audio, model_link_one, outputTextQ, error_queue))
    model_process_two = multiprocessing.Process(target=trans_model, args=(input_audio, model_link_two, outputTextQ, error_queue))
    model_process_three = multiprocessing.Process(target=trans_model, args=(input_audio, model_link_three, outputTextQ, error_queue))

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

    while not outputTextQ.empty():
        results.append(outputTextQ.get())
    
    print(results)
    
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

    print(decision_counts)

    # Check for at least 2 out of 3 agreement
    for result, count in decision_counts.items():
        if count >= 2:
            testsPass = True
            testPassed = result

    # Putting translated test on textQ
    if testsPass == True and testPassed != None:
        text_queue.put(testPassed)

