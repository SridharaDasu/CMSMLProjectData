## Util
This folder contains script that conatin global utility functions that can be used as standalone or as imports

### Data Reader
The file contains code to read the data in various formats and generate data from the genMLProjectData executable.

#### CSV Reader
The class object is used to read csv data in various formats.

| Functions | Definition |
| ------ | ------ |
| read_csv_to_df | Reads the data (with file path provided) as a pandas dataframe |
| read_csv_to_dict | Reads the data as a simple python dictionary |

#### Data Stream
The class object is generate data from the genMLPorjectData executable which shal be subsequently used for training

| Functions | Definition |
| ------ | ------ |
| single_packet | Generates a single 256 event data packet (translates to 256 datapoints).Set the REGION_TYPE in accordance with the data expected from the executable |
| generate_data | Generates an n number of above single packets and saves them as a single file containing all data with an extra column mem_batch to differentiate between the packets data |