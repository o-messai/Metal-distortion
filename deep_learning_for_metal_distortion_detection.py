# -*- coding: utf-8 -*-
"""Deep learning for Metal distortion detection.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1O0Y0T3WzLa0rV6XRCsBCOBuy2IOcg4ec

## Deep learning for Metal distortion detection
"""

!nvidia-smi

# Commented out IPython magic to ensure Python compatibility.
# Connect to drive folder to use the dataset (The dataset is publicily available)
from google.colab import drive
drive.mount('/content/drive')
# %cd '/content/drive/MyDrive/Colab Notebooks/Fault detection'
!ls

from tensorflow.compat.v1 import ConfigProto
from tensorflow.compat.v1 import InteractiveSession

config = ConfigProto()
# config.gpu_options.per_process_gpu_memory_fraction = 0.5
config.gpu_options.per_process_gpu_memory_fraction = 1
config.gpu_options.allow_growth = True
session = InteractiveSession(config=config)

# import the libraries as shown below

import tensorflow as tf
import datetime
import matplotlib.pyplot as plt
from tensorflow.keras import optimizers
from tensorflow.keras.layers import Input, Lambda, Dense, Flatten
from tensorflow.keras.models import Model, load_model
from tensorflow.keras.applications.inception_v3 import InceptionV3
from keras.applications.vgg16 import VGG16
from tensorflow.keras.applications.inception_v3 import preprocess_input
from tensorflow.keras.preprocessing import image
from tensorflow.keras.preprocessing.image import ImageDataGenerator,load_img
from tensorflow.keras.models import Sequential
from tensorflow.keras.applications import MobileNetV3Small
from tensorflow.keras.applications import MobileNetV3Large
from tensorflow.keras.applications import EfficientNetB7 
from tensorflow.keras.applications import DenseNet201
import numpy as np
from glob import glob

# re-size all the images to this
IMAGE_SIZE = [200, 200]

train_path = '/content/drive/MyDrive/Colab Notebooks/Fault detection/uploads/Database/Train'
valid_path = '/content/drive/MyDrive/Colab Notebooks/Fault detection/uploads/Database/Test'

# Choose the pre-trained model

# Import the Vgg 16 library as shown below and add preprocessing layer to the front of VGG
# Here we will be using imagenet weights
my_net = DenseNet201(input_shape=IMAGE_SIZE + [3], weights='imagenet', include_top=False)
#inception = InceptionV3(input_shape=IMAGE_SIZE + [3], weights='imagenet', include_top=False)
#my_vgg16 = VGG16(input_shape=IMAGE_SIZE + [3], weights='imagenet', include_top=False)
#my_mobileNET = MobileNetV3Large(input_shape=IMAGE_SIZE + [3], weights='imagenet', include_top=False)
#my_efficent_Net = EfficientNetB7(input_shape=IMAGE_SIZE + [3], weights='imagenet', include_top=False)

# don't train existing weights
count = 0
for layer in my_net.layers:
    layer.trainable = True
    count += 1
print('Total number of layers: {}'.format(count))

# useful for getting number of output classes
folders = glob('/content/drive/MyDrive/Colab Notebooks/Fault detection/uploads/Database/Train/*')
# our layers - you can add more if you want
# x = Flatten()(inception.output)
# x = Flatten()(my_vgg16.output)
# x = Flatten()(my_mobileNET.output)
x = Flatten()(my_net.output)
print(x)

prediction = Dense(len(folders), activation='softmax')(x)

# create a model object
# model = Model(inputs=inception.input, outputs=prediction)
# model = Model(inputs=my_vgg16.input, outputs=prediction)
# model = Model(inputs=my_mobileNET.input, outputs=prediction)
model = Model(inputs=my_net.input, outputs=prediction)

#Package to view the model structure 
!pip install visualkeras

# view the structure of the model
# model.summary()
import visualkeras

#visualkeras.layered_view(model).show() # display using your system viewer
visualkeras.layered_view(model, to_file='model.png').show() # write and show
display(file="model.png")

# tell the model what cost and optimization method to use

model.compile(
  loss='categorical_crossentropy',
  optimizer=optimizers.Adam(learning_rate=0.001),
  metrics=['accuracy']
)

# Use the Image Data Generator to import the images from the dataset
train_datagen = ImageDataGenerator(rescale = 1./255,
                                   shear_range = 0.2,
                                   zoom_range = 0.2,
                                   horizontal_flip = True,
                                   vertical_flip=True)

test_datagen = ImageDataGenerator(rescale = 1./255)

# Make sure you provide the same target size as initialied for the image size
training_set = train_datagen.flow_from_directory(train_path,
                                                 target_size = (200, 200),
                                                 batch_size = 32,
                                                 class_mode = 'categorical')

test_set = test_datagen.flow_from_directory(valid_path,
                                            target_size = (200, 200),
                                            batch_size = 360,
                                            class_mode = 'categorical')

# Commented out IPython magic to ensure Python compatibility.
# Load the TensorBoard notebook extension
# %load_ext tensorboard
# Clear any logs from previous runs
!rm -rf ./logs/ 
!rm -rf ./Checkpoint/ 
log_dir = "logs/fit/" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
log_model = "Checkpoint/" + datetime.datetime.now().strftime("%Y%m%d-%H")
tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir=log_dir, histogram_freq=1)
models_callback = tf.keras.callbacks.ModelCheckpoint(log_model, verbose=1, save_best_only=True)

# fit the model
# Run the cell. It will take some time to execute
r = model.fit(
  training_set,
  validation_data=test_set,
  epochs=10,
  steps_per_epoch=len(training_set),
  validation_steps=len(test_set),
  callbacks=[models_callback])

#@title
# plot the loss
!ls
plt.plot(r.history['loss'], label='Training loss')
plt.plot(r.history['val_loss'], label='Validation loss')
plt.legend()
plt.title('Training and validation loss')
plt.show()
plt.savefig('LossVal_loss')

# plot the accuracy
plt.plot(r.history['accuracy'], label='Training accuracy')
plt.plot(r.history['val_accuracy'], label='Validation accuracy')
plt.title('Training and validation accuracy')
plt.legend()
plt.show()
plt.savefig('AccVal_acc')

# save it as a h5 file
# model.save('model_inception.h5')
# model.save('model_vgg16.h5')
# model.save('model_mobileNet.h5')
# model.save('my_efficent_Net.h5') 
#model_2 = load_model('model_inception.h5')

loaded_model = load_model(log_model)
loaded_model.save('my_net.h5')

