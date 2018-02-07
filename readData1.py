import pandas as pd # interpret and manipulate data
from ggplot import *
#Read data with proper headers
monitor = pd.read_csv('C:/Users/Alain/Documents/Zhou/hAAT/Monitor2.txt',sep='\t',names=['reading', 'date', 'time', 'valid', \
'unknown1', 'unknown2', 'unknown3', 'unknown4', 'unknown5', 'unknown6', \
'1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16', \
'17','18','19','20','21','22','23','24','25','26','27','28','29','30','31','32'])

#Drop first 10 non-movement data columns
monitor = monitor.drop(monitor.columns[range(10)],axis=1)

#Drop any columns that are all zeroes
monitor = monitor.loc[:, (monitor != 0).any(axis=0)]

monitor.index.name = 'time'
monitor['time'] = monitor.index
monitor.reset_index(drop=True)

monitor = monitor.drop(['4','8','12','16','20','24','28'],axis=1)

data = pd.melt(monitor, id_vars='time')
plot = ggplot(data, aes(x='time',weight='value')) + geom_bar() + scale_y_continuous(limits=(0,150))
plot.show()
