from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Flatten
from tensorflow.keras.layers import Conv2D, MaxPooling2D
from tensorflow.keras import backend as K
import numpy as np
import json
import pandas as pd
import matplotlib.pyplot as plt
import pywt
import keras
import tensorflow


class cnn:


    def __init__(self, batch_size, epochs, dim1, dim2, channels, num_classes):

        self.batch_size = batch_size
        self.epochs = epochs
        self.dim1 = dim1
        self.dim2 = dim2
        self.channels = channels
        self.num_classes = num_classes
        self.input_shape = (self.dim1, self.dim2, self.channels)


    def data_preprocessing(self, signal, noise):

        signal = np.log(signal)
        noise = np.log(noise)
        data = np.concatenate((signal, noise), axis=0)
        labels = np.concatenate((np.ones(len(signal)), np.zeros(len(noise))),axis=0)
        x_train, x_test, y_train, y_test = train_test_split(data, labels, test_size=0.30, random_state=20)
        x_train = x_train.reshape(x_train.shape[0], self.dim1, self.dim2, self.channels)
        x_test = x_test.reshape(x_test.shape[0], self.dim1, self.dim2, self.channels)
        x_train = x_train.astype('float32')
        x_test = x_test.astype('float32')
        y_train = keras.utils.to_categorical(y_train,2)
        y_test = keras.utils.to_categorical(y_test,2)

        return x_train, x_test, y_train, y_test



    def cnn_model(self):


        #define sequential model
        model = Sequential()
        model.add(Conv2D(32, kernel_size=(3, 3),
                         activation='relu',
                         input_shape=self.input_shape))
        model.add(Conv2D(64, (3, 3), activation='relu'))
        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(Dropout(0.25))
        model.add(Flatten())
        model.add(Dense(128, activation='relu'))
        model.add(Dropout(0.5))
        model.add(Dense(self.num_classes, activation='sigmoid'))

        model.compile(loss=tensorflow.keras.losses.binary_crossentropy,
                  optimizer=tensorflow.keras.optimizers.Adadelta(),
                  metrics=['accuracy'])

        return model



    def train_history(self, model, x_train, y_train, x_test, y_test):

        history = model.fit(x_train, y_train,
              batch_size=self.batch_size,
              epochs=self.epochs,
              verbose=1,
              validation_data=(x_test, y_test))

        return history


    def model_evaluate(self, model, x_test, y_test,):

         score = model.evaluate(x_test, y_test, verbose=0)
         print('Test loss', score[0])
         print('Test accuracy', score[1])




if __name__ == "__main__":

    signal = np.load('./signal.npy')
    noise = np.load('./noise.npy')

    model = cnn(128,2500,50,50,1,2)
    x_train, x_test, y_train, y_test = model.data_preprocessing(signal, noise)
    cnn = model.cnn_model()

    history = model.train_history(cnn,x_train,y_train,x_test,y_test)

    model.model_evaluate(cnn, x_test, y_test)

    ##serialize model to json
    model_to_json = cnn.to_json()
    with open('model.json','w') as json_file:
        json_file.write(model_to_json)

    #serialize model to HDF5
    cnn.save_weights('cnn.h5')
    print('model saved to disk')

    f, (ax1, ax2) = plt.subplots(2,1, figsize=(10,6))
    f.subplots_adjust(hspace=0.5)
    ax1.plot(history.history['accuracy'])
    ax1.plot(history.history['val_accuracy'])
    ax1.set_title('Model accuracy')
    ax1.set_ylabel('Accuracy')
    ax1.set_xlabel('Epoch')
    ax1.legend(['Train', 'Test'], loc='upper right')

    ax2.plot(history.history['loss'])
    ax2.plot(history.history['val_loss'])
    ax2.set_title('Model loss')
    ax2.set_ylabel('Loss')
    ax2.set_xlabel('Epoch')
    ax2.legend(['Train', 'Test'], loc='upper right')

    plt.show()
    plt.close()
