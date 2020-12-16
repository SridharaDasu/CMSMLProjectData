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

4. The `EDA_generatedData.ipynb` file contains the code performing Exploratory Data Analysis on the generated mock data.
To run the notebook, run the following command in the directory with the notebook at the Terminal (Mac/Linux) or Command Prompt (Windows):

```jupyter notebook```
