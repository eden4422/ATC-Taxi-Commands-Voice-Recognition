import tkinter
import time
import multiprocessing
from commands import *
import Mongo_Read_Data
import JSON_to_Mongo
import json
import tempfile
import fasteners
import shutil
from ttkthemes import ThemedStyle

onlyRecentMode = True
autoUpdateCommand = True
# For a lot of this, reference this page on stackexchange: https://stackoverflow.com/questions/29158220/tkinter-understanding-mainloop
# also this one for general tkinter stuff https://realpython.com/python-gui-tkinter/

# I think the best bet for updating the commands from the JSON would be to use things found here: https://www.geeksforgeeks.org/how-to-get-file-creation-and-modification-date-or-time-in-python/
# To detect if the file has changed or not on a particular check. If the file has been modified, then update the contents of the text box.
# ALSO ABOUT TEXT BOXES on instantiation the text boxes will have to be set to disabled,and then if anything needs to be changed in them enable, change, disable, or else
# The user will be able to type in there >:(

# This whole section is really just formatting
window = tkinter.Tk()

style = ThemedStyle(window)
style.set_theme("equilux")

containingFrame = tkinter.Frame(master=window)
topFrame = tkinter.Frame(master=containingFrame)
bottomFrame = tkinter.Frame(master=containingFrame)
speechBoxFrame = tkinter.Frame(master=topFrame)
speechBoxLabel = tkinter.Label(master=speechBoxFrame, text="All Speech")
commandsBoxFrame = tkinter.Frame(master=topFrame)
commandsBoxLabel = tkinter.Label(master=commandsBoxFrame, text="Commands")
allSpeechBox = tkinter.Text(master=speechBoxFrame, width=40, height=25, borderwidth=1, relief="raised")
commandsBox = tkinter.Text(master=commandsBoxFrame, width=40, height=25, borderwidth=1, relief="raised")
muteButton = tkinter.Button(master=bottomFrame, text="Unmute", width = 6)
startButton = tkinter.Button(master=bottomFrame, text="Start")
autoUpdateCommandButton = tkinter.Button(master=bottomFrame, text="Auto Update: On")
endButton = tkinter.Button(master=bottomFrame, text="End")
pullRecentButton = tkinter.Button(master=bottomFrame, text="Most Recent")
pullAllCommandsButton = tkinter.Button(master=bottomFrame, text="All Commands")
containingFrame.pack(padx=5, pady=5, fill=tkinter.BOTH, expand=True)
topFrame.pack(fill=tkinter.BOTH, expand=True)
bottomFrame.pack(fill=tkinter.BOTH)
speechBoxFrame.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True)
commandsBoxFrame.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True)
speechBoxLabel.pack()
commandsBoxLabel.pack()
allSpeechBox.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True)
commandsBox.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True)
muteButton.pack(side=tkinter.LEFT)
startButton.pack(side=tkinter.LEFT)
#autoUpdateCommandButton.pack(side=tkinter.LEFT)
endButton.pack(side=tkinter.LEFT)
pullRecentButton.pack(side=tkinter.LEFT)
pullAllCommandsButton.pack(side=tkinter.LEFT)

# Create a function to clear the text from the allSpeechBox
def clear_all_speech():
    allSpeechBox.config(state="normal")
    allSpeechBox.delete("1.0", tkinter.END)
    allSpeechBox.config(state="disabled")

# Create a button that will call the clear_all_speech function when clicked
clearAllSpeechButton = tkinter.Button(master=bottomFrame, text="Clear All Speech", command=clear_all_speech)
clearAllSpeechButton.pack(side=tkinter.LEFT)


#______________________________________________________________________________________
# Create a new frame for the flight id input
flightIdFrame = tkinter.Frame(master=window)  # Change containingFrame to window
flightIdLabel = tkinter.Label(master=flightIdFrame, text="Flight ID")
flightIdBox = tkinter.Text(master=flightIdFrame, width=20, height=1, borderwidth=1, relief="raised")  # Reduced width

def overwrite_json():
    flight_id = flightIdBox.get("1.0", "end-1c")
    data = {"flight_id": flight_id}

    # Create a lock file
    lock = fasteners.InterProcessLock('flight_id.json.lock')

    with lock:
        # Create a temporary file and write the data to it
        with tempfile.NamedTemporaryFile('w', delete=False) as f:
            json.dump(data, f)
            tempname = f.name

        # Rename the temporary file to flight_id.json
        # This operation is atomic, so flight_id.json will never be empty
        shutil.move(tempname, 'flight_id.json')

    flightIdBox.delete("1.0", tkinter.END)

overwriteButton = tkinter.Button(master=flightIdFrame, text="Change ID", command=overwrite_json)  # Change bottomFrame to flightIdFrame

# Pack the new elements into the GUI
flightIdFrame.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)
flightIdLabel.pack()
flightIdBox.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True)
overwriteButton.pack(side=tkinter.LEFT)  # This will now pack the overwriteButton into the flightIdFrame



#make sure your event handler appears above any bindings, or it won't recognize it
#put handlers in here for organization
def handle_mute_click(event):
    #I assume the easiest thing to do would just be to stop accepting input from the mic, or turn it off
    if muteButton.cget("text") == "Unmute":
        muteButton.config(text="Mute")
        queueOut.put((MUTE, "Unmuted"))
    else:
        muteButton.config(text="Unmute")
        queueOut.put((MUTE, "Muted"))

def handle_start_click(event):
    queueOut.put((START, "Start"))

def handle_end_click(event):
    queueOut.put((KILLCHILDREN, "End"))

def handle_pull_all(event):
    commandsBox.config(state="normal")
    # do your query here and stick it in the variable
    text_to_put = Mongo_Read_Data.View_All()
    commandsBox.delete("1.0", tkinter.END)
    commandsBox.insert(tkinter.END, text_to_put)
    commandsBox.config(state="disabled")
    global onlyRecentMode
    onlyRecentMode = False

def handle_pull_recent(event):
    commandsBox.config(state="normal")
    # do your query here and stick it in the variable
    text_to_put = Mongo_Read_Data.View_Most_Recent()
    commandsBox.delete("1.0", tkinter.END)
    commandsBox.insert(tkinter.END, text_to_put)
    commandsBox.config(state="disabled")
    global onlyRecentMode
    onlyRecentMode = True

def handle_auto_update(event):
    global autoUpdateCommand
    if autoUpdateCommand == True:
        autoUpdateCommand = False
        autoUpdateCommandButton.config(text="Auto Update: Off")
    else:
        autoUpdateCommand = True
        autoUpdateCommand.config(text="Auto Update: On")

#This is how you bind something. The first argument is the event that you want something to happen on (left click in this case),
#and the second is what you want to have happen.
#Please put all your bindings here
button1 = "<Button-1>"
muteButton.bind(button1, handle_mute_click)
startButton.bind(button1, handle_start_click)
autoUpdateCommandButton.bind(button1, handle_auto_update)
endButton.bind(button1, handle_end_click)
pullAllCommandsButton.bind(button1, handle_pull_all)
pullRecentButton.bind(button1, handle_pull_recent)

#--------------------------------------------------------------------------------------------------------------------------------------
#Tkinter demo of some functionality that I need for reference.
# myLabel = tkinter.Label(text="0")
# #myLabel.pack()

# class Timing:
#     def __init__(self, myLabel):
#         self.myLabel = myLabel
#     def doThing(self):
#         self.myLabel.config(text= int(myLabel.cget("text")) + 2)
#         #for this .after() spins up a second thread to run and do an activity after a specified period of time. In this case, it is 
#         #executing doThing() after two seconds (2000ms). This functionality can be used for checking the JSON for updates if you don't
#         #want to check every window loop. This example just has it up the number in the label by 2 every two seconds.
#         self.myLabel.after(2000, self.doThing)
# # make your timer, tell it to do the thing.
# timer = Timing(myLabel)
# timer.doThing()
#--------------------------------------------------------------------------------------------------------------------------------------

queueIn = multiprocessing.Queue()
queueOut = multiprocessing.Queue()

class functionality:
    prev_time = 0
    curr_time = 1
    def __init__(self, window, c_box, a_box):
        self.window = window
        self.c_box = c_box
        self.a_box = a_box
        self.counter = 1
    def do_functionality(self):
        # this is where we route to specific functionality
        #self.checkDoCommandUpdate()
        #self.checkDoAllSpeechUpdate()
        #self.checkDoErrorUpdate()
        while not queueIn.empty():
            command_to_do = queueIn.get()
            if command_to_do[0] == 1:
                self.check_do_error_update(command_to_do)
            elif command_to_do[0] == 2:
                self.check_do_all_speech_update(command_to_do)
            elif command_to_do[0] == 3:
                self.check_do_error_update(command_to_do)
            elif command_to_do[0] ==4 and autoUpdateCommand:
                self.check_do_command_update(command_to_do)
        self.window.after(100, self.do_functionality)
        
    def check_do_command_update(self, command_to_do):
        #example of updating. Instead of doing a counter, check the JSON
        # self.cBox.config(state="normal")
        
        # self.cBox.delete("1.0", tkinter.END)
        # self.counter = self.counter + 1
        # self.cBox.insert(tkinter.END, self.counter)


        # This can be used for checking if the commands JSON file has been updated. It'll need the name of the file
        # It checks the modification time of the file, and assigns it to the currTime variable. If currTime does not match
        # prevTime (the last time it was updated) then it will set the prevTime to currTime, open the file, read it to the
        # fileContents string variable, and then stick it into the text box. The file is then closed.
        # closing the file is probably excessive since it will only read, but eh.
        # When the JSON saving is worked out itll have to be changed to properly parse the JSON and stuff but thats not too
        # bad to change.
        # self.currTime = os.stat('testyText.txt').st_mtime
        # if self.currTime != self.prevTime:
        #     self.prevTime = self.currTime
        #     myFile = open('testyText.txt', "r")
        #     fileContents = myFile.read()
        # change so instead of deleting it just adds the thing
        ##     self.cBox.delete("1.0", tkinter.END)
        #     self.cBox.insert(tkinter.END, fileContents)
        #     myFile.close()
        # self.cBox.config(state="disabled")

        #depending on the mode its in, itll do a different thing.
        if onlyRecentMode:
            # do your query here and stick it in the variable
            text_to_put = Mongo_Read_Data.View_Most_Recent()
            commandsBox.delete("1.0", tkinter.END)
            commandsBox.insert(tkinter.END, text_to_put)
            commandsBox.config(state="disabled")
        else:
            commandsBox.config(state="normal")
            # do your query here and stick it in the variable
            text_to_put = Mongo_Read_Data.View_All()
            commandsBox.delete("1.0", tkinter.END)
            commandsBox.insert(tkinter.END, text_to_put)
            commandsBox.config(state="disabled")

    def check_do_all_speech_update(self, command):
        # stick them into the text box
        self.a_box.config(state="normal")
        self.a_box.insert(tkinter.END, "\n" + command[1])
        self.a_box.config(state="disabled")

    def check_do_error_update(self, command):
        #This is set up to add to the box, if you want to change it to 
        self.e_box.config(state="normal")
        self.e_box.insert(tkinter.END, "\n" + command[1])
        self.e_box.config(state="disabled")

        

# main loop must be here or it'll freak. if its above stuff itll end up skipping things :/
#all other stuff goes here, above the main loop.

def get_going(inyago, outyago):
    global queueIn
    global queueOut
    queueIn = inyago
    queueOut = outyago
    commandsBox.config(state="disabled")
    allSpeechBox.config(state="disabled")
    do_funct = functionality(window, commandsBox, allSpeechBox)
    do_funct.do_functionality()
    window.mainloop()

# queue has a tuple with the type of thing and the actual stuff in the second element
# 

#getGoing()

# doFunct = functionality(window, commandsBox, allSpeechBox, errorBox)
# doFunct.doFunctionality()
# window.mainloop()

