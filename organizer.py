import os
import time
from pathlib import Path

from tkinter import *
from tkinter import filedialog

####### UI #######
originalFolder = ""
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


## Run code
    def runCode():
        global originalFolder 
        originalFolder = txt.get()
        scanDirFiles(os.scandir(txt.get()), txt1.get(), float(txt2.get()), dropdown.get())
        root.destroy()

    runBtn = Button(root, text="Run", command=runCode)
    runBtn.grid(column=2, row=3, padx=5, pady=10)
# execute tkinter
    root.mainloop()




####### LOGIC #######

def scanDirFiles(directoryFiles, destinationPath, timeThreshold, timeUnitThreshold):    
    for file in directoryFiles:
        if file.is_file():
            timeSinceModification = time.time() - os.path.getmtime(file.path)
            timeUnit = "seconds"
            
            timeSinceModification, timeUnit = fixTimeUnit(timeSinceModification)
            
            organize(file, destinationPath, timeSinceModification, timeUnit, timeThreshold, timeUnitThreshold)

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
        print(f"destinationPath: {destinationPath}, folderPath: {folderPath}")
        if os.path.exists(f"{destinationPath}/old_{folderPath}"):
            os.rename(file.path, f"{destinationPath}/old_{folderPath}/{file.name}")
        else:
            os.makedirs(f"{destinationPath}/old_{folderPath}")
            os.rename(file.path, f"{destinationPath}/old_{folderPath}/{file.name}")

def findRelativePath(file, originalDir):
    relativePath = Path(os.path.dirname(file.path)).relative_to(originalDir)
    return relativePath



# Run the file
UI()