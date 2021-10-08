import os
import matplotlib.pyplot as plt
from Python.util.data_reader import DataStream
import numpy as np

# all paths relative to main dir
IMAGE_PATH = './images'

def render_plot(data, mem_batch, event, pod='electron'):
    """
    data: data output from the data generator or loaded data in pandas dataframe format
    pod: part of 16 bit data: electron bit, tau bit, et to be plotted
    mem_batch: int in range of n, where n is the no. of datapoints/files generated using data gen
    event: 0-255 int range
    """

    event_data = data[(data['mem_batch'] == mem_batch) & (data['event'] == event)].copy()

    x_elec = np.array(event_data[pod])
    matrix_electron = np.asmatrix(x_elec)

    # Resizing into size 14x18
    matrix_electron.resize((14, 18))
    fig, ax = plt.subplots(figsize = (18, 6))
    mat = ax.imshow(matrix_electron, cmap='GnBu', interpolation='nearest')

    # Set attributes
    plt.ylabel("eta")
    plt.xlabel("phi")
    plt.yticks(range(matrix_electron.shape[0]))
    plt.xticks(range(matrix_electron.shape[1]))
    plt.title('Electron regions on 14x18 2D plot (event '+str(event)+')')

    # this places 0 or 1 centered in the individual squares
    for x in range(matrix_electron.shape[0]):
        for y in range(matrix_electron.shape[1]):
            ax.annotate(str(matrix_electron[x, y])[0], xy=(y, x), 
                        horizontalalignment='center', verticalalignment='center')
    
    fig.savefig("%s/%s" % (IMAGE_PATH,"Event_"+str(event)+"_"+pod+".png"))
    plt.show()