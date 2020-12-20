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

6. The `Event_Clustering.ipynb` file contains the code performing Exploratory Data Analysis and Model Development on the generated mock data.
To run the notebook, run the following command in the directory with the notebook at the Terminal (Mac/Linux) or Command Prompt (Windows):

```jupyter notebook```
