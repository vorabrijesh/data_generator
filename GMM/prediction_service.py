import requests
import time, json, random
import numpy as np
import tensorflow as tf
from flask import Flask, request, session, render_template

from pymongo import MongoClient
app = Flask(__name__)
app.secret_key = "prediction_service"


def get_pred(data):  
    print("Loading the model..")
    global loaded_model 
    loaded_model = tf.keras.models.load_model("ML_MODEL")
    print("Loaded the model from disk \n\n")
    print(loaded_model.summary())  

    client = MongoClient('localhost', 27017)
    workflow =client['kali_db']['kali_wf']
    images = data['images']['content']    
    images = images.replace('[','')
    images = images.replace(']','')
    images = images.replace('\n','')
    images = images.replace(',','')
    images = images.split(' ')
    images = np.array(images, dtype=np.float64)
    
    images = np.reshape(images,(int(images.shape[0]/784),28,28))
    
    predictions = loaded_model.predict_classes(images)
    
    print(predictions)
    # labels = np.reshape(labels,(int(labels.shape[0]/784),28,28))
    target_class = int(data['target_class']['content'])
    extracted_data = images[np.where(predictions==target_class)]
    extracted_data = extracted_data.flatten()
    print(extracted_data)
    predictions = str(predictions)
    
    try:
        client = MongoClient('localhost',27017)
        workflow =client['kali_db']['kali_wf']
        data['msg'] = {'type':'text','content':'gmm_predictions'}
        # data['predictions'] = {'type':'text','content':str(predictions)}
        data['extracted_data'] = {'type':'text','content':str(list(extracted_data))}
        workflow.insert_one(data)
        print("Predictions sent to workflow")
    except:
        print("Predictions failed to be sent")
    return "1"


@app.route('/model', methods= ['GET', 'POST'])
def model():
    data = request.get_json()
    # print(data)
    
    if(data['msg']['content']=='gmm_images'):
        get_pred(data)
    return "1"

if __name__ == "__main__":
    app.run(port=5008,debug=True)
