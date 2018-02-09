import pandas as pd # interpret and manipulate data
from plotnine import * # plot data
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import Image
import os


class Window(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.data = None
        self.sampleList = []
        self.image = None
        self.plot = None
        self.interval = ''
        self.statistic = tk.StringVar()
        self.monitor = None
        self.browserFile = None
        self.sampleObjects = None

        mainFrame=tk.LabelFrame(borderwidth=0,highlightthickness=0)
        mainFrame.grid()

        entryFrame = ttk.LabelFrame(mainFrame, text='File Entry', height=800)
        entryFrame.grid(row=0,column=0)

        # File browsing
        fileEntry = ttk.Entry(entryFrame,width=50)
        fileEntry.grid(row=0,column=0,columnspan=10)

        fileBrowseButton = ttk.Button(entryFrame, text="Browse", command = lambda: browser())
        fileBrowseButton.grid(row=0,column=11)

        # Recording intervals
        intervalFrame = ttk.LabelFrame(mainFrame, text='Interval')
        intervalFrame.grid(row=1)
        intervalLabel = ttk.Label(intervalFrame, text='Time: ')
        intervalLabel.grid(row=1,column=0)
        self.time = tk.StringVar()
        intervalEntry = ttk.Entry(intervalFrame,width=10, textvariable = self.time)
        intervalEntry.grid(row=1,column=1,stick='w')
        self.unit_of_time=tk.StringVar()
        intervalOption = ttk.OptionMenu(intervalFrame, self.unit_of_time, *['Select Unit','Seconds','Minutes','Hours','Days'])
        intervalOption.grid(row=1,column=2)

        # choice of statistic
        statisticFrame = ttk.LabelFrame(mainFrame, text='Statistic')
        statisticFrame.grid(row=2)
        statisticLabel = ttk.Label(statisticFrame, text='Please choose a statistic: ')
        statisticLabel.grid(row=0,column=0)
        statisticOption = ttk.OptionMenu(statisticFrame, self.statistic, *['Mean','Mean','Sum'])
        statisticOption.grid(row=0,column=1)


        # Plot
        plotButton = ttk.Button(mainFrame, text="Plot", command = lambda: plot(self.interval, self.statistic))
        plotButton.grid(row=3,column=0,columnspan=11,pady=20)

        #create canvas
        plotLabelFrame = ttk.LabelFrame(text='Plot')
        plotLabelFrame.grid(row=0,column=1,rowspan=100)
        canvas = tk.Canvas(plotLabelFrame, width=750, height=750)
        canvas.grid()


        def browser():
            browserFile = tk.filedialog.askopenfilename(initialdir = os.getcwd(),title = "Select file",filetypes = (("txt files","*.txt"),("all files","*.*")))
            fileEntry.delete(0, tk.END)
            fileEntry.insert(0, browserFile)
            self.browserFile = browserFile


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
            self.monitor = monitor

            # sum up data columns (exclude 'time' column)
            self.sampleList= list(monitor)
            self.sampleList.remove('time')


            self.sampleObjects = []
            sampleFrame = ttk.LabelFrame(text='Samples found')
            sampleFrame.grid(row=4,stick='e')

            class sample:
                def __init__(self, checkValue, labelName, rowNum, colNum):
                    self.checkValue = tk.IntVar(value=checkValue)
                    self.labelName = labelName

                    self.Check = ttk.Checkbutton(sampleFrame, variable = self.checkValue, command = lambda: updateSelected())
                    self.Check.grid(row=rowNum, column=colNum, padx=(10,0),stick='e')

                    self.Label = ttk.Label(sampleFrame, text=self.labelName)
                    self.Label.grid(row=rowNum, column=colNum+1, padx=(0,10), pady=(10),stick='w')

            for counter, i in enumerate(self.sampleList):
                self.sampleObjects.append(sample(1, str(i), counter+3, 3))

        def updateSelected():
            self.sampleList = []
            for i in self.sampleObjects:
                if i.checkValue.get() == 1:
                    self.sampleList.append(i.labelName)
            print(self.sampleList)

        def plot(interval,statistic):
            # If all information is available, plot.
            def plotSuccess():

                #standard deviation
                self.monitor['std'] = self.monitor[self.sampleList].std(1)
                #unbiased standard error
                self.monitor['se'] = self.monitor[self.sampleList].sem(1)

                if self.statistic.get() == 'Sum':
                    self.monitor['value'] = self.monitor[self.sampleList].sum(1)
                    print(self.monitor)
                elif self.statistic.get() == 'Mean':
                    self.monitor['value'] = self.monitor[self.sampleList].mean(1)
                    # for error bars
                    self.monitor['ymin'] = self.monitor['value'] - self.monitor['se']
                    self.monitor['ymax'] = self.monitor['value'] + self.monitor['se']
                    print(self.monitor)

                self.data = self.monitor

                if self.statistic.get() == 'Mean':
                    self.plot = (ggplot(self.data, aes(x='time',weight='value')) + geom_bar() + \
                    geom_errorbar(aes(x='time',ymax='ymax',ymin='ymin'),color='red',size=1,width=1) + \
                    #geom_point(aes(x='time',y='4')) + \
                    scale_x_continuous(breaks=range(0,48,2)) + \
                    xlab('Time (hours)') + ylab('Movements detected') + \
                    ggtitle('Fly movement over time (' + str(len(self.sampleList)) + ' samples)\nRecording Interval: ' + self.interval))

                elif self.statistic.get() == 'Sum':
                    self.plot = (ggplot(self.data, aes(x='time',weight='value')) + geom_bar() + \
                    #geom_point(aes(x='time',y='4')) + \
                    scale_x_continuous(breaks=range(0,48,2)) + \
                    xlab('Time (hours)') + ylab('Movements detected') + \
                    ggtitle('Fly movement over time (' + str(len(self.sampleList)) + ' samples)\nRecording Interval: ' + self.interval))

                # save plot
                self.plot.save('plot.png', width=20,height=20,units='cm')

                # create GUI elements for plot and resize plot image

                """img = Image.open('plot.png')
                img = img.resize((750,750), Image.ANTIALIAS)
                img.save('plot.png','PNG')"""
                img = tk.PhotoImage(file='plot.png')
                self.image = img
                canvas.create_image(375, 375, image=self.image)

            # Check for missing information.
            if self.monitor is not None:
                if self.time.get() != '' and self.unit_of_time.get() != 'Select Unit':
                    self.interval = self.time.get() + ' ' + self.unit_of_time.get()
                    plotSuccess()
                else:
                    tk.messagebox.showinfo('Missing Information','Time interval incomplete.')
            else:
                tk.messagebox.showinfo('Missing Information','No file selected.')

if __name__ == '__main__':
    root= tk.Tk()
    Window(root).grid()
    root.mainloop()
