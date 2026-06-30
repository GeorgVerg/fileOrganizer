import os
import time

import threading
from pathlib import Path

from tkinter import *
from tkinter import filedialog

####### UI #######
originalFolder = ""
currentlyOrganizing = ""
def UI():
# create box
    root = Tk()
    root.title("File Organizer")
    root.geometry("700x200+400+350")

# create content

## Set folder path
    lbl = Label(root, text="Which file do you want to organize?", font=("Arial Bold", 12))
    lbl.grid(sticky="w", padx=10, pady=10)

    txt = Entry(root, width=20)
    txt.grid(column=1, row=0, sticky='nsew')

    def selectFolder():
        dir = filedialog.askdirectory()
        txt.insert(0, dir)

    openBtn = Button(root, text="Select Folder", command=selectFolder)
    openBtn.grid(column=2, row=0, sticky='w', padx=10, pady=10)


## Set destination path
    lbl1 = Label(root, text="Where do you want to move the older files?", font=("Arial Bold", 12))
    lbl1.grid(column=0, row=1, sticky='w', padx=10, pady=10)

    txt1 = Entry(root, width=20)
    txt1.grid(column=1, row=1, sticky='nsew')

    def selectDestinationFolder():
        dir = filedialog.askdirectory()
        txt1.insert(0, dir)

    openBtn1 = Button(root, text="Select Folder", command=selectDestinationFolder)
    openBtn1.grid(column=2, row=1, sticky='w', padx=10, pady=10)


## Set time threshold
    lbl2 = Label(root, text="Enter time since last modification:", font=("Arial Bold", 12))
    lbl2.grid(column=0, row=2, sticky='w', padx=10, pady=10)

    txt2 = Entry(root, width=20)
    txt2.grid(column=1, row=2, sticky='nsew')

    dropdown = StringVar(root)
    dropdown.set("minutes") # default value
    timeOptions = ["seconds", "minutes", "hours", "days", "years"]
    timeDropdown = OptionMenu(root, dropdown, *timeOptions)
    timeDropdown.grid(column=2, row=2, sticky='w', padx=10, pady=10)


    def loadingWindow():
        cacheInfo = [
            txt.get(),
            txt1.get(),
            txt2.get(),
            dropdown.get()
        ]
        root.destroy()
        loadingRoot = Tk()
        loadingRoot.title("File Organizer")
        loadingRoot.geometry("400x200+400+350")
        loadingLbl = Label(loadingRoot, text="Organizing files...", font=("Arial Bold", 16))
        loadingLbl.pack(pady=20)

        currentlyOrganizingLbl = Label(loadingRoot, text=f"Currently organizing: {os.path.basename(cacheInfo[0])}", font=("Arial Bold", 12))
        currentlyOrganizingLbl.pack(pady=10)

        thread = threading.Thread(target=scanDirFiles, args=(os.scandir(cacheInfo[0]), cacheInfo[1], float(cacheInfo[2]), cacheInfo[3]))
        
        def updateCurrentlyOrganizingLbl():
            currentlyOrganizingLbl.config(text=("Currently organizing: " + currentlyOrganizing))
            if thread.is_alive():
                loadingRoot.after(500, updateCurrentlyOrganizingLbl)
            else:
                loadingRoot.after(1000, loadingRoot.destroy)

        thread.start()
        updateCurrentlyOrganizingLbl()

        loadingRoot.mainloop()
        


## Run code
    def runCode():
        if txt.get() != "" and txt1.get() != "" and txt2.get() != "":
            global originalFolder 
            originalFolder = txt.get()
            
            loadingWindow()
        elif txt.get() == txt1.get():
            errorLbl = Label(root, text="You can't organize files into the same folder.", font=("Arial Bold", 12), fg="red")
            errorLbl.grid(column=1, row=3, sticky='nsew', padx=10, pady=10)
        else:
            errorLbl = Label(root, text="Please fill in all fields.", font=("Arial Bold", 12), fg="red")
            errorLbl.grid(column=1, row=3, sticky='nsew', padx=10, pady=10)

    runBtn = Button(root, text="Run", command=runCode)
    runBtn.grid(column=2, row=3, padx=5, pady=10)
# execute tkinter
    root.mainloop()




####### LOGIC #######

def scanDirFiles(directoryFiles, destinationPath, timeThreshold, timeUnitThreshold):    
    for file in directoryFiles:
        if file.is_file():
            updateCurrentlyOrganizing(file)

            timeSinceModification = time.time() - os.path.getmtime(file.path)
            timeUnit = "seconds"
            
            timeSinceModification, timeUnit = fixTimeUnit(timeSinceModification)
            
            organize(file, destinationPath, timeSinceModification, timeUnit, timeThreshold, timeUnitThreshold)

            time.sleep(0.1)

        elif file.is_dir():
            scanDirFiles(os.scandir(file.path), destinationPath, timeThreshold, timeUnitThreshold)

def fixTimeUnit(timeSinceModification):
    if timeSinceModification > 60:
        timeSinceModification = timeSinceModification / 60
        timeUnit = "minutes"
        if timeSinceModification > 60:
            timeSinceModification = timeSinceModification / 60
            timeUnit = "hours"
            if timeSinceModification > 24:
                timeSinceModification = timeSinceModification / 24
                timeUnit = "days"
                if timeSinceModification > 365:
                    timeSinceModification = timeSinceModification / 365
                    timeUnit = "years"

    timeSinceModification = round(timeSinceModification, 2)
    return timeSinceModification, timeUnit

def organize(file, destinationPath, timeSinceModification, timeUnit, timeThreshold, timeUnitThreshold):
    folderPath = findRelativePath(file, Path(originalFolder).parent)
    if timeSinceModification > timeThreshold and timeUnit == timeUnitThreshold:
        if os.path.exists(f"{destinationPath}/old_{folderPath}"):
            os.rename(file.path, f"{destinationPath}/old_{folderPath}/{file.name}")
        else:
            os.makedirs(f"{destinationPath}/old_{folderPath}")
            os.rename(file.path, f"{destinationPath}/old_{folderPath}/{file.name}")

def findRelativePath(file, originalDir):
    relativePath = Path(os.path.dirname(file.path)).relative_to(originalDir)
    return relativePath


def updateCurrentlyOrganizing(file):
    global currentlyOrganizing
    currentlyOrganizing = file.name


# Run the file
UI()