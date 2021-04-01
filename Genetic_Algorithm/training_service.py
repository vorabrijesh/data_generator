import requests
import time, json, random
import numpy as np
import tensorflow as tf
from flask import Flask, request, session

from pymongo import MongoClient
app = Flask(__name__)
app.secret_key = "training_service"


def load():
    print("Loading the model..")
    # loaded_model = tf.keras.models.load_model("ML_Model")
    global loaded_model 
    loaded_model = tf.keras.models.load_model("ML_MODEL")
    print("Loaded the model from disk \n\n")
    print(loaded_model.summary())
    return "1"

@app.route('/retrain', methods= [ 'GET','POST'])
def get_data():
    data = request.get_json()
    # print(data)
    
    if(data['msg']['content']=='retrain'):
        retrain(data['synthetic_data']['content'], data['epochs']['content'])
    return "1"


def retrain(synthetic_data, epochs):
    load()
    
    synthetic_data = synthetic_data.split(',')
    synthetic_data = np.array(synthetic_data, dtype=np.float64)
    print(synthetic_data.shape)
    synthetic_data = np.reshape(synthetic_data,(8,784))
    synthetic_labels = loaded_model.predict_classes(synthetic_data)
    print("\nSynthetic data received from server")
    # retrain the model
    loaded_model.fit(synthetic_data, verbose=1, epochs= int(epochs))
    
    print('Training Completed')
    return "1"


if __name__ == "__main__":
    app.run(port=5003,debug=True)
