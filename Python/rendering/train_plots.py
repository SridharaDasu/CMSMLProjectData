import json
import matplotlib.pyplot as plt
import numpy as np

hist_path = './Python/models/results/train_plots/'
model_name = 'fc_dnn'
file_path = hist_path+model_name+'_history.json'
history = json.load(open(file_path,'rb'))
# list all data in history
print(history.keys())
for key in history.keys():
    history[key] = np.array(list(history[key].values()))

# summarize history for mse metric
plt.plot(history['msle'])
plt.plot(history['val_msle'])
plt.title('%s model msle' % model_name)
plt.ylabel('mse')
plt.xlabel('epoch')
plt.legend(['train', 'val'], loc='upper left')
plt.savefig(hist_path+model_name+'_msle.png')
plt.show()

# summarize history for loss
plt.plot(history['loss'])
plt.plot(history['val_loss'])
plt.title('%s model loss' % model_name)
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'val'], loc='upper left')
plt.savefig(hist_path+model_name+'_loss.png')
plt.show()