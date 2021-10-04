### CMS Experiment Model

1. Start by creating a virtual environment for installing the libraries.

```python3 -m virtualenv venv```

**Note:** If you have not installed the virtualenv library, you can do so by running:

```python3 -m pip install --user virtualenv```

2. Activate the environment.

	For Windows:

	```
	cd venv/Scripts
	activate
	```

	For MacOS/Linux:

	```source env/bin/activate```

3. Go back to the root directory and install the requirements.txt.

```pip install -r requirements.txt```

4. We will be using Jupyter Notebook to run our code. You can install it using pip.

```pip install notebook```

5. To generate the data, use the code and follow the instructions from [here](https://github.com/SridharaDasu/CMSMLProjectData).

You can create a new folder 'output_data' to store the generated mock data by running the following code.

```
genMLProjectData --background=232341231 --write=BackgroundRegionData.txt --dump=output_data/BackgroundRegionData.csv
genMLProjectData --background=987654323 --electron=50 --write=ElectronRegionData.txt --dump=output_data/ElectronRegionData.csv
genMLProjectData --background=478343223 --tau=50 --write=TauRegionData.txt --dump=output_data/TauRegionData.csv
```

6. To run the notebook, run the following command in the directory with the notebook at the Terminal (Mac/Linux) or Command Prompt (Windows):

```jupyter notebook```


##### About the notebooks

1. The '1. get_uct_borders.ipynb' gets the tuple value of the 4x4 border regions of the original 72x56 data values.
2. The '2. get_event_data.ipynb' is just a helper notebook to retrieve data for a single event.
3. The '3. Merge_module.ipynb' uses our custom module 'merger.py' to merge the value of energies in bordering regions with True signal values.
4. The '4. select_and_sort.ipynb' implements the selection and sorting of data to reduce its dimensions.
5. The '5. jet_merge.ipynb' implements the merging, selection and sorting of jet data to reduce its dimensions.

###### Other

- The `Event_Clustering.ipynb` file contains the code performing Exploratory Data Analysis and Model Development for a single event of the electron region data.
- The `Electron_data_clustering.ipynb` file contains the code performing Exploratory Data Analysis and Model Development for all events of the electron region data.
- The `Exploratory_data_analysis_all.ipynb` file contains the code performing Exploratory Data Analysis on the generated mock data.
- The 'Merge_Energies.ipynb' file contains the code for merging the values of energy for neighbouring signal values.
