from os import name
import keras
from keras import layers, Model
from keras.layers import Dense, Layer, LocallyConnected1D
import tensorflow as tf

ENCODING_DIM = 3

def fc_dnn(ip_dim=252, load_wt = None):
    """
    Fully Connected DNN Autoencoder Model
    Total params: 38,108
    Trainable params: 38,108
    """

    flat_input = keras.Input(shape=(ip_dim,), name="input_layer")
    encoded = Dense(64, activation='relu', name='hle_one')(flat_input)
    encoded = Dense(32, activation='relu', name='hle_two')(encoded)

    ls_layer = Dense(16, activation='relu', name='ls_layer')(encoded)

    decoded = Dense(32, activation='relu', name='hld_two')(ls_layer)
    decoded = Dense(64, activation='relu', name='hld_one')(decoded)
    decoded = Dense(ip_dim, activation='sigmoid', name='output_layer')(decoded)

    # This model maps an input to its reconstruction
    model = Model(flat_input, decoded, name='fc_dnn_ae')
    if load_wt:
       model.load_weights(load_wt)
   
    model.summary()

    return model

def spc_dnn(ip_dim=252, load_wt = None):

   """
   Model Info:
   input_layer --> hle_one: 252 to 64: 64*(4 + 1) = 320 params    (256 w/o bias)
   hle_one --> hle_two: 64 to 32: 32*(4 + 1) = 160 params         (128 w/o bias)
   hle_two --> ls_layer: 32 to 16: 16*32 + 16 = 528 params        (512 w/o bias)
   ls_layer --> hld_two: 16 to 32: 32*16 + 32 = 544 params        (512 w/o bias)
   hld_two --> hld_one: 32 to 64: 64*(2 + 1) = 192 params         (128 w/o bias)
   hld_one --> output_layer: 64 to 252: 256 + 252 = 508 params    (256 w/o bias)
   Total Params:
   Total params: 2,252 (~16 times lower)
   """

   f = 4
   input = keras.layers.Input(shape=(ip_dim,), name="input_layer")

   #First Encoding Layer (4 neurons to 1: stride 4)
   encode1lt =  []
   steps = (ip_dim-f)//4 + 1  #stride = 4
   for i in range(steps):
      encode1lt.append(Dense(1, activation='relu')(input[:, i*4:(i+1)*4]))
   
   #Adding the 64th neuron (252/4=63)
   encode1lt.append(Dense(1, activation='relu')(input[:,-4:]))
   encoded = keras.layers.concatenate(encode1lt, name="hle_one")

   #Second Encoding Layer (4 neurons to 1: stride 2)
   encode2lt =  []
   steps = (64-f)//2 +1       #stride = 2
   for i in range(steps):
      encode2lt.append(Dense(1, activation='relu')(encoded[:, i*2:(i+2)*2]))
   
   #Adding the 32nd neuron (252/4=63)
   encode2lt.append(Dense(1, activation='relu')(encoded[:,-4:]))
   encoded = keras.layers.concatenate(encode2lt, name="hle_two")

   ls_layer = Dense(16, activation='relu', name='ls_layer')(encoded)
   
   ## Decoder
   decoded = Dense(32, activation='relu', name='hld_two')(ls_layer)

   decoded2lt = []
   steps = (ip_dim-f)//4 + 1
   for x in range(steps):
      if(x < 2):
         # First two neurons are connected to first ls_layer neuron only
         decoded2lt.append(Dense(1, activation='relu')(decoded[: , 0:1]))
      else:
         idx = x//2
         decoded2lt.append(Dense(1, activation='relu')(decoded[: , idx-1:idx+1]))
   
   decoded2lt.append(Dense(1, activation='relu')(decoded[:,-4:]))
   decoded = keras.layers.concatenate(decoded2lt, name="hld_one")

   outputlt = []
   for i in range(ip_dim-1):
      idx = i//4
      outputlt.append(Dense(1, activation='relu')(decoded[:, idx:idx+1]))

   outputlt.append(Dense(1, activation='relu')(decoded[:,-5:]))
   output = keras.layers.concatenate(outputlt, name="output_layer")
   model = keras.models.Model(input, output)
   if load_wt:
       model.load_weights(load_wt)

   model.summary()

   return model

def pc_dnn(ip_dim=252, load_wt = None):
   """
   Fully connecting only several internal blocks in sets of f == 4.
   Total params: 10,572 (~ 4 times smallers)
   """

   model = 0
   f = 4
   input = keras.layers.Input(shape=(ip_dim,), name="input_layer")
   block_size = ip_dim//f
   encode1lt = []
   for idx in range(f):
      # Connecting 63 neurons to 16 neurons and making 4 such sets (63*4 ---> 16*4)
      encode1lt.append(Dense(16, activation='relu')(input[: , idx*block_size:(idx+1)*block_size]))
   
   encoded = keras.layers.concatenate(encode1lt, name="hle_one")

   encode2lt = []
   block_size = 64//f
   for idx in range(f):
      # Connecting 16 neurons to 8 neurons and making 4 such sets (16*4 ---> 8*4)
      encode2lt.append(Dense(8, activation='relu')(encoded[: , idx*block_size:(idx+1)*block_size]))
   
   encoded = keras.layers.concatenate(encode2lt, name="hle_two")

   ls_layer = Dense(16, activation='relu', name='ls_layer')(encoded)
   
   ## Decoder
   decoded = Dense(32, activation='relu', name='hld_two')(ls_layer)

   decode1lt = []
   block_size = 32//f
   for idx in range(f):
      # Connecting 8 neurons to 16 neurons and making 4 such sets (16*4 <--- 8*4)
      decode1lt.append(Dense(16, activation='relu')(decoded[: , idx*block_size:(idx+1)*block_size]))
   
   decoded = keras.layers.concatenate(decode1lt, name="hld_one")

   outputlt = []
   block_size = 64//f
   for idx in range(f):
      # Connecting 16 neurons to 64 neurons and making 4 such sets (63*4 <--- 16*4)
      outputlt.append(Dense(63, activation='relu')(decoded[: , idx*block_size:(idx+1)*block_size]))
   
   output = keras.layers.concatenate(outputlt, name="output_layer")
   model = keras.models.Model(input, output)
   if load_wt:
       model.load_weights(load_wt)
       
   model.summary()

   return model
