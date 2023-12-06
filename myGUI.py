import tkinter
import time
# For a lot of this, reference this page on stackexchange: https://stackoverflow.com/questions/29158220/tkinter-understanding-mainloop
# also this one for general tkinter stuff https://realpython.com/python-gui-tkinter/

# I think the best bet for updating the commands from the JSON would be to use things found here: https://www.geeksforgeeks.org/how-to-get-file-creation-and-modification-date-or-time-in-python/
# To detect if the file has changed or not on a particular check. If the file has been modified, then update the contents of the text box.
# ALSO ABOUT TEXT BOXES on instantiation the text boxes will have to be set to disabled,and then if anything needs to be changed in them enable, change, disable, or else
# The user will be able to type in there >:(

# This whole section is really just formatting
window = tkinter.Tk()
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
endButton = tkinter.Button(master=bottomFrame, text="End")
errorBox = tkinter.Text(master=bottomFrame, width=30, height=15, borderwidth=1, relief="raised")

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
endButton.pack(side=tkinter.LEFT)
errorBox.pack(side=tkinter.LEFT, fill=tkinter.X, expand=True)


#make sure your event handler appears above any bindings, or it won't recognize it
#put handlers in here for organization
def handleMuteClick(event):
    if muteButton.cget("text") == "Unmute":
        muteButton.config(text="Mute")
    else:
        muteButton.config(text="Unmute")

#This is how you bind something. The first argument is the event that you want something to happen on (left click in this case),
#and the second is what you want to have happen.
#Please put all your bindings here
muteButton.bind("<Button-1>", handleMuteClick)

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

class functionality:
    def __init__(self, window, cBox, aBox, eBox):
        self.window = window
        self.cBox = cBox
        self.aBox = aBox
        self.eBox = eBox
        self.counter = 1
    def doFunctionality(self):
        # this is where we route to specific functionality
        self.checkDoCommandUpdate()
        self.checkDoAllSpeechUpdate()
        self.checkDoErrorUpdate()
        self.window.after(1000, self.doFunctionality)
        
    def checkDoCommandUpdate(self):
        #example of updating. Instead of doing a counter, check the JSON
        self.cBox.config(state="normal")
        self.cBox.delete("1.0", tkinter.END)
        self.counter = self.counter + 1
        self.cBox.insert(tkinter.END, self.counter)
        self.cBox.config(state="disabled")

    def checkDoAllSpeechUpdate(self):
        pass

    def checkDoErrorUpdate(self):
        pass

        

# main loop must be here or it'll freak. if its above stuff itll end up skipping things :/
#all other stuff goes here, above the main loop.

def getGoing():
    commandsBox.config(state="disabled")
    allSpeechBox.config(state="disabled")
    errorBox.config(state="disabled")
    doFunct = functionality(window, commandsBox, allSpeechBox, errorBox)
    doFunct.doFunctionality()
    window.mainloop()

#getGoing()

# doFunct = functionality(window, commandsBox, allSpeechBox, errorBox)
# doFunct.doFunctionality()
# window.mainloop()