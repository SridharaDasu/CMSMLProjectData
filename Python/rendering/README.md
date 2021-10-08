## Rendering
This folder contains script for rendering any visuals/plots that can be imported in modules or run as standalone codes

### Eta-Phi Plot
The file contains code to generate eta phi plot over data generated using the genMLProjectData code. The data is imported as a pandas dataframe using the datareader in the util models.

| Params | Definition |
| ------ | ------ |
| Data | The data (generated as a result of generate data in Data Stream) loaded as a Pandas dataframe |
| Mem_batch | The value of mem_batch column in the data, of the rows, which we need to select|