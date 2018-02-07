import pandas as pd # interpret and manipulate data
from ggplot import * # plot data

# Recording intervals
interval = '30 minutes'

data = None
number = 0

#Read data with proper headers
monitor = pd.read_csv('Monitor2.txt',sep='\t',names=['reading', 'date', 'time', 'valid', \
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

# drop data columns after summing
monitor = monitor.drop(col_list,axis=1)

# format data for ggplot
data = pd.melt(monitor, id_vars='time')
print(data)
# plot
plot = ggplot(data, aes(x='time',weight='value')) + geom_bar() + \
scale_x_continuous(breaks=range(0,48,2)) + \
labs(x='Time (hours)',y='Movements detected') + \
ggtitle('Fly movement over time (' + str(number) + ' samples)\nRecording Interval: ' + interval)

# save plot
plot.show()
