import os
import pandas as pd
import numpy as np
import pickle
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


DIM = (14, 18)   # Eta x Phi

def raw_to_matrix(data, save_path=None):
    """data: pandas dataframe of the raw data generated from the data.py file"""
    net_data = []
    mem_batch = data.mem_batch.unique()
    events = data.event.unique()
    for mb in mem_batch:
        print(mb)
        df_mb = data[data.mem_batch == mb]
        for en in events:
            df_en = df_mb[df_mb.event == en]
            mat = np.array(df_en.et)
            mat.resize(DIM)
            net_data.append(mat)
    
    net_data = np.array(net_data)
    
    if save_path:
        np.save(save_path+'data_raw_2d.npy', net_data, allow_pickle=True, fix_imports=True)

    return net_data

def scaler(dataset, save_path=None, use_new=True):
    if use_new:
        sc=StandardScaler()
        dataset = sc.fit_transform(dataset)
    else:
        sc = pickle.load(open(save_path,'rb'))
        dataset = sc.transform(dataset)

    if save_path:
        pickle.dump(sc, open(save_path, 'wb'))
    
    return dataset

def xy_dataset(bgdata, adata, split=0.2, scale=True, save_path=None):
    """Take in background and anomaly (electron/tau) data and outputs data in x y format with split"""
    """Input 1D formatted data (simple reshape)"""
    ad_labels = np.ones(adata.shape[0])
    bg_labels = np.zeros(bgdata.shape[0])
    feature_data = np.concatenate((bgdata,adata), axis=0)
    target_data = np.concatenate((bg_labels,ad_labels), axis=0)

    x_train, x_test, y_train, y_test = train_test_split(feature_data, target_data, test_size=split, stratify=target_data)
    
    # Keeping only background data
    bg_index = np.where(y_train==0)
    x_train = x_train[bg_index]
    y_train = y_train[bg_index]

    if scale:
        # Scaling operation
        print('Performing Scaling Function')
        x_train = scaler(x_train, save_path='./Python/models/results/scaler.pkl')
        x_test = scaler(x_test, save_path='./Python/models/results/scaler.pkl', use_new=False)
    
    if save_path:
        np.save(save_path+'x_train.npy', x_train, allow_pickle=True, fix_imports=True)
        np.save(save_path+'x_test.npy', x_test, allow_pickle=True, fix_imports=True)
        np.save(save_path+'y_train.npy', y_train, allow_pickle=True, fix_imports=True)
        np.save(save_path+'y_test.npy', y_test, allow_pickle=True, fix_imports=True)

    return x_train, x_test, y_train, y_test


# Simple Raw Data data  Generator
if __name__=='__main__':
    #data = pd.read_csv('./Python/data/ELECTRONdata_raw.csv')
    #data = raw_to_matrix(data, save_path='./Python/data/ELECTRON')

    bgdata = np.load('./Python/data/BACKGROUNDdata_raw_2d.npy')
    bgdata = bgdata.reshape(bgdata.shape[0], int(bgdata.shape[1]*bgdata.shape[2]))
    adata = np.load('./Python/data/ELECTRONdata_raw_2d.npy')
    adata = adata.reshape(adata.shape[0], int(adata.shape[1]*adata.shape[2]))

    xy_dataset(bgdata, adata, split=0.2, scale=True, save_path='./Python/data/splitdata/')
