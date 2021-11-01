import os
import pandas as pd
import numpy as np
import csv
import subprocess
from random import sample

EXE_PATH = './genMLProjectData.exe'
DATA_PATH = './Python/data/'


class CSVReader():

    def read_csv_to_df(self, file_path):
        # Read CSV data to pandas dataframe
        df = pd.read_csv(file_path)
        return df

    def read_csv_to_dict(self, file_path):
        # Read CSV data to dictionary format
        with open(file_path, mode='r') as csv_ip:
            reader = csv.reader(csv_ip)
            data_dict = {rows[0]: rows[1] for rows in reader}
            return data_dict


class DataStream():
    # Region Type: BACKGROUND, ELECTRON, TAU
    # --electron=50 --write=ElectronRegionData.txt --compare=ElectronRegionData.ref --dump=ElectronRegionData.csv

    def single_packet(self, seed, REGION_TYPE='BACKGROUND'):
        # generate single packet data: 256 events/ 1 file
        if REGION_TYPE=='BACKGROUND':
            subprocess.call(["genMLProjectData.exe", "--background="+str(seed), "--write="+DATA_PATH+REGION_TYPE+
                        "RegionData.txt", "--dump="+DATA_PATH+REGION_TYPE+"RegionData.csv"], stdout=subprocess.DEVNULL)
        elif REGION_TYPE=='ELECTRON':
            subprocess.call(["genMLProjectData.exe", "--background="+str(seed), '--electron=50', "--write="+DATA_PATH+REGION_TYPE+
                        "RegionData.txt", "--dump="+DATA_PATH+REGION_TYPE+"RegionData.csv"], stdout=subprocess.DEVNULL)
        elif REGION_TYPE=='TAU':
            subprocess.call(["genMLProjectData.exe", "--background="+str(seed), '--tau=50', "--write="+DATA_PATH+REGION_TYPE+
                        "RegionData.txt", "--dump="+DATA_PATH+REGION_TYPE+"RegionData.csv"], stdout=subprocess.DEVNULL)

    def generate_data(self, data_num, REGION_TYPE='BACKGROUND'):
        seeds = sample(range(999999999), data_num)
        data = pd.DataFrame()
        csv_reader = CSVReader()
        for idx in range(data_num):
            self.single_packet(seeds[idx], REGION_TYPE)
            file_path = DATA_PATH+REGION_TYPE+"RegionData.csv"
            datapoint = csv_reader.read_csv_to_df(file_path)
            datapoint['mem_batch'] = idx
            data = data.append(datapoint)
            data.reset_index(inplace=True, drop=True)
        data.to_csv(DATA_PATH+REGION_TYPE+"data_raw.csv", index=False)
        
        return data