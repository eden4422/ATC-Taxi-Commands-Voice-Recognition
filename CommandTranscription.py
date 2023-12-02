# python library imports
import multiprocessing
import queue

# local imports
from ModelOne import model_one
from ModelTwo import model_two
from ModelThree import model_three


def transcribe_audio(input_audio,text_queue, error_queue):
    
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

