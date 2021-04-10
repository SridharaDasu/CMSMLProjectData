# Importing necessary libraries
import numpy as np
import logging
from skimage.util import view_as_blocks

# Logger
log = logging.getLogger(__name__)

def get_matrix(event_data, column):
    """
    Function to get matrix data from a series of column.
    
    Args:
        event_data: Dataframe containing event data
        column: Name of column to get the matrix for
    Returns: 
        numpy matrix of size 14x18.
    """
    # Initialize
    x_data = np.array([])
    
    if column != 'index':
        # Convert the series into a numpy matrix
        x_data = np.array(event_data[column])
        
    else:
        x_data = np.array(event_data.index.to_list())

    # Convert the series into a numpy matrix
    matrix_data = np.asmatrix(x_data)

    # Resizing into size 14x18
    matrix_data.resize((14, 18))
    
    return matrix_data


def get_energy_sums(event_data):
    """
    Get the energy sums of 2x2 sub regions along with their indices.
    
    Args:
        event_data: Dataframe containing event data
        
    Returns:
        Dictionary of values 'index': sum
    """
    # Empty dictionary
    sum_energy_index = {}
    
    # Configuring the size of sub regions
    s = 2

    # We will now get 2x2 sub matrices as blocks from the electron matrix.
    # Reshape each matrix into a list format.
    blocks_energy = view_as_blocks(get_matrix(event_data, 'et'), (s,s)).reshape(-1,s**2)

    # We will now get 2x2 sub matrices as blocks from the index matrix.
    # Reshape each matrix into a list format.
    blocks_idx = view_as_blocks(get_matrix(event_data, 'index'), (s, s)).reshape(-1,s**2)
    
    for row, (sub, idx) in enumerate(zip(blocks_energy, blocks_idx)):
        # Add all energies in 2x2 region
        sum_energy = np.sum(sub)
        # get the actual index of the highest postion of energy in the submatrix (2x2)
        actual_idx = idx[np.argmax(sub)]

        sum_energy_index[actual_idx] = sum_energy
        
    return sum_energy_index

def select_and_sort_jet_data(event_data):
    """
    Function to sort and select limited amount of values from rows containing energy (with True signals).
    Args:
        event_data: Dataframe containing event data
        signal: Type of signal data ['electron', 'tau']
    Returns:
        event_data_final: Dataframe containing the specified number of reduced data by selection and sorting.
    """
    # Number of data rows to select
    selection = 6
    # Get a copy of original dataframe
    event_data_final = event_data.copy()
    
    # Get list of energy and their actual indices
    energy_index_list = get_energy_sums(event_data)
    
    # replace the new values of energy based on index
    event_data_final.loc[list(energy_index_list.keys()),'et'] = list(energy_index_list.values())
    
    for idx in event_data_final.index.to_list():
        # if the index is not in our prev list of energy values
        # electron does not exist in this index
        if idx not in energy_index_list.keys():
            event_data_final.loc[idx, 'et']= 0
    
    # Get non-zero values
    event_data_final = event_data_final[event_data_final['et']!=0]
    
    # Sort them and select top 6 values
    event_data_final = event_data_final.sort_values(by='et', ascending=False)[:selection]
    
    return event_data_final