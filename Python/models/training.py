import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from keras.callbacks import ModelCheckpoint, EarlyStopping
from models import fc_dnn, pc_dnn, spc_dnn

EPOCHS = 200
BATCH_SIZE = 512
VAL_SPLIT = 0.2
MODEL_PATH = './Python/models/results/'
MODEL_NAME = 'spc_dnn_rd_20'
PT_PATH = './Python/models/results/pt_weights/'  # Keep the pretrained weights in this folder
PT_MODEL_NAME = 'spc_dnn'

if __name__=='__main__':
    # Importing Processed Data
    data_path = './Python/data/h5xydata/'
    x_train = np.load(data_path+'x_train.npy')
    y_train = np.load(data_path+'x_test.npy')

    # Creating a new model
    #model = fc_dnn(load_wt=PT_PATH+'weights_%s.h5' % PT_MODEL_NAME)
    model = spc_dnn()

    #saving model architecture
    model_arch = model.to_json()
    with open(MODEL_PATH+MODEL_NAME+'.json','w') as json_file:
        json_file.write(model_arch)

    model.compile(loss='mse', metrics=['msle'], optimizer='adam')
    chk = ModelCheckpoint(MODEL_PATH+'weights_%s.h5' % MODEL_NAME, monitor='val_loss', mode='min', save_best_only=True, save_weights_only=True, verbose=1)
    es = EarlyStopping(monitor='val_loss', mode='min', verbose=1, patience=3)

    history = model.fit(
        x_train,
        x_train,
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        validation_split=VAL_SPLIT,  # This makes the net split as 64:16:20 (train:val:test)
        callbacks=[chk,es])
    
    # convert the history.history dict to a pandas DataFrame:     
    hist_df = pd.DataFrame(history.history)

    # save to json:  
    hist_json_file = MODEL_PATH+MODEL_NAME+'_history.json' 
    with open(hist_json_file, mode='w') as f:
        hist_df.to_json(f)
