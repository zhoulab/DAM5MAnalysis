import pandas as pd # interpret and manipulate data
from ggplot import * # plot data
from tkinter import *
from tkinter import ttk
from PIL import Image
import os


root = Tk()
root.title("Drosophila Movement Interpreter")

# File browsing
fileEntry = ttk.Entry(root,width=70)
fileEntry.grid(row=0,column=0)

fileBrowseButton = ttk.Button(root, text="Browse", command = lambda: browser())
fileBrowseButton.grid(row=0,column=1)

# Recording intervals
intervalLabel = ttk.Label(root, text='Interval Time: ')
intervalLabel.grid(row=1,column=0)
interval = StringVar()
intervalEntry = ttk.Entry(root,width=10, textvariable = interval)
intervalEntry.grid(row=1,column=1)

# allow for selection of samples
samples = []

# Plot
image = None
plotButton = ttk.Button(root, text="Plot", command = lambda: plot(data,number,interval))
plotButton.grid(row=2,column=0)

#create canvas
plotLabelFrame = ttk.LabelFrame(text='Plot')
plotLabelFrame.grid(row=3,column=2,rowspan=10)
canvas = Canvas(plotLabelFrame, width=725, height=800)
canvas.grid()

data = None
number = 0

def browser():
    global data
    global number
    browserFile = filedialog.askopenfilename(initialdir = os.getcwd(),title = "Select file",filetypes = (("txt files","*.txt"),("all files","*.*")))
    fileEntry.delete(0, END)
    fileEntry.insert(0, browserFile)

    #Read data with proper headers
    monitor = pd.read_csv(browserFile,sep='\t',names=['reading', 'date', 'time', 'valid', \
    'unknown1', 'unknown2', 'unknown3', 'unknown4', 'unknown5', 'unknown6', \
    '1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16', \
    '17','18','19','20','21','22','23','24','25','26','27','28','29','30','31','32'])

    #Drop first 10 non-movement data columns
    monitor = monitor.drop(monitor.columns[range(10)],axis=1)

    #Drop any columns that are all zeroes
    monitor = monitor.loc[:, (monitor != 0).any(axis=0)]

    # change index to time
    monitor.index.name = 'time'
    monitor['time'] = monitor.index
    monitor.reset_index(drop=True)

    # sum up data columns (exclude 'time' column)
    col_list= list(monitor)
    col_list.remove('time')
    monitor['sum'] = monitor[col_list].sum(1)
    number = len(col_list)

    samples = col_list
    sampleObjects = []

    class sample:
        def __init__(self, checkValue, labelName, rowNum, colNum):
            self.checkValue = IntVar(value=checkValue)
            self.labelName = labelName

            self.Check = Checkbutton(root, variable = self.checkValue, command = lambda: updateSelected())
            self.Check.grid(row=rowNum, column=colNum, padx=(10,0),stick='e')

            self.Label = ttk.Label(root, text=self.labelName)
            self.Label.grid(row=rowNum, column=colNum+1, padx=(0,10), pady=(10),stick='w')

    for counter, i in enumerate(col_list):
        sampleObjects.append(sample(1, str(i), counter+3, 3))


    # drop data columns after summing
    monitor = monitor.drop(col_list,axis=1)

    # format data for ggplot
    data = pd.melt(monitor, id_vars='time')



def plot(data,number,interval):
    global image
    # plot
    plot = ggplot(data, aes(x='time',weight='value')) + geom_bar() + \
    scale_x_continuous(breaks=range(0,48,2)) + \
    labs(x='Time (hours)',y='Movements detected') + \
    ggtitle('Fly movement over time (' + str(number) + ' samples)\nRecording Interval: ' + interval.get())

    # save plot
    plot.save('plot.png')

    # create GUI elements for plot and resize plot image

    img = Image.open('plot.png')
    img = img.resize((750,750), Image.ANTIALIAS)
    img.save('plot.png','PNG')
    img = PhotoImage(file='plot.png')
    image = img
    canvas.create_image(325, 400, image=image)

root.mainloop()
