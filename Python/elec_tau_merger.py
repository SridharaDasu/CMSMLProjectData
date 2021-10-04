# Importing necessary libraries
import numpy as np
import logging

# Logger
log = logging.getLogger(__name__)

# We will be using this list to find if any signal bits i.e, Electron = True values have these positions.
# If they do, we will be merging the value of their energy.
horizontal_list_border = [(0, 3), (4, 7), (8, 11), (12, 15)]
vertical_list_border = [(15, 3), (14, 2), (13, 1), (12, 0)]

def merge_adjacent_energy(matrix_signal, matrix_energy, matrix_position):
    """
    Merge the value of energies if they lie in border regions.
    Find adjacent electron True bits and 
    check if their position matches our horizontal or vertical list of bordering positions.
    
    Args:
    matrix_signal: 
    matrix_energy:
    matrix_position:
    horizontal_list_border:
    vertical_list_border:
    
    Returns: Series of new energy values.
    """
    # Set initial value of prev val as 0
    prev_val = 0
    energy_values = np.array(matrix_energy)
    # Loop through rows of the electron values
    for i, row in enumerate(np.array(matrix_signal)):

        # Loop through value of electron in each row of the matrix
        for j, val in enumerate(row):

            # If the signal value is 1
            if val == 1:

                # Check if previous value was also 1
                if val == prev_val:

                    # Get the value of energy (ET) of both the positions
                    pos1 =  matrix_position.item(i, j-1)
                    pos2 =  matrix_position.item(i, j)

                    pos_set = (pos1, pos2)
                    
                    if pos_set in horizontal_list_border or pos_set in vertical_list_border:
                        # Position set lies on the edge of UCT region
                        log.info("Border Match found:", pos_set)

                        log.info("Match Coord 1: (%s , %s)" % (i, j-1))
                        # Merge the energies
                        energy_values = merge_function(matrix_energy, i, j) 

            # Set the value of previous value as current value for next iteration
            prev_val = val
    return energy_values


def merge_function(matrix_et, i, j):
    """
    Merge the value of energies.
    """
    energy_array = np.array(matrix_et)
    # Get the value of energy (ET) of both the positions
    energy1 =  matrix_et.item(i, j-1)
    energy2 =  matrix_et.item(i, j)
   
    log.info("Merging energies:")
    log.info("Energy1:", energy1)
    log.info("Energy2:", energy2)

    # If the first position contains higher ET, merge the energy of both the positions and save it in that position
    if energy1>energy2:
        energy_array[i, j-1] = energy_array[i, j-1] + energy_array[i, j]
        energy_array[i, j] = 0 # Set ET of next position as 0

    # If the second position contains higher ET, merge the energy of both the positions and save it in that position
    elif energy1<energy2:
        energy_array[i, j] = energy_array[i, j-1] + energy_array[i, j]
        energy_array[i, j-1] = 0 # Set ET of previous position as 0

    # If the ETs are equal, merge the energy of both the positions and save it in left(first) position
    elif energy1==energy2:

        energy_array[i, j-1] = energy_array[i, j-1] + energy_array[i, j]
        energy_array[i, j] = 0 # Set ET of next position as 0
        
    return energy_array