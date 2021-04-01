import requests
import time, json, random
import numpy as np
import tensorflow as tf
from flask import Flask, request, session

from pymongo import MongoClient
app = Flask(__name__)
app.secret_key = "client"


# STEP 1: LOADING THE MODEL FROM DISK **************************
def load():
    print("Loading the model..")
    # loaded_model = tf.keras.models.load_model("ML_Model")
    global loaded_model 
    loaded_model = tf.keras.models.load_model("ML_MODEL")
    print("Loaded the model from disk \n\n")
    print(loaded_model.summary())
    return "1"



# STEP 2: SEND REQUEST TO BEGIN TRAINING ***************************
def start_training(data):
    session['id'] = str(int(random.random()*1000))
    print(session['id'])   
    print("Sending request to begin training")
    test_data = str(data['class']['content'])
    # print(data)
    data['id'] ={'type' :'text', 'content':session['id']}
    
    data['msg']['content'] = 'start_training'
    data['test_data'] = {'type' :'text', 'content':test_data}
    
    try:
        client = MongoClient('localhost',27017)
        workflow =client['kali_db']['kali_wf']
        
        # print(data)
        workflow.insert_one(data)
        # print('inserted',data)
    except:
        print("Request completed \n")
    return "1"
    
    

# STEP 3: GET IMAGES FROM SERVER AND SEND PREDICTIONS TO SERVER *****************
# @app.route('/p', methods=['GET','POST'])
def get_pred(images, target_class):
    
    images = images.replace('[','')
    images = images.replace(']','')
    images = images.replace('\n','')
    images = images.replace(',','')
    images = images.split(' ')
    images = np.array(images, dtype=np.float64)
    
    images = np.reshape(images,(8,28,28))
    # print(images[0])
    # print("Shape of received images: ", images.shape)

    predictions = loaded_model.predict(images)
    # print('shape of prediction sahpe', predictions.shape)
   
    # predictions = str(predictions)
    
    try:
        client = MongoClient('localhost',27017)
        workflow =client['kali_db']['kali_wf']
        data = {}
        data['msg'] = {'type':'text','content':'predictions'}
        # print('target_class', target_class)
        # print(predictions[target_class].shape)
        data['predictions'] = {'type':'text','content':str(predictions[:,target_class])}
        #data1 = json.dumps(data)
        # print('checkpoint')
        workflow.insert_one(data)
        print("Predictions sent to server")
    except:
        print("Predictions failed to be sent")
    return "1"


#  START TRAINING  FROM CLIENT   ************************************************
# @app.route('/train',methods=['GET','POST'])
def train():
    load()
    start_training()
    return "1"
    
    
@app.route('/model', methods= ['GET', 'POST'])
def model():
    data = request.get_json()
    # print(data)
    
    if (data['msg']['content'] =='start_session'):
        load()
        start_training(data)
    if(data['msg']['content']=='images'):
        images = data['images']['content']
        target_class = int(data['target_class']['content'])
        get_pred(images, target_class)
    if(data['msg']['content']=='retrain'):
        synthetic_data(data['synthetic_data']['content'])
    return "1"


# STEP 4: REQUESTING THE SYNTHETIC DATA FROM THE SERVER*************************
# @app.route('/synthetic_data',methods=['GET','POST'])
def synthetic_data(synthetic_data):
    synthetic_data = synthetic_data.replace('[','')
    synthetic_data = synthetic_data.replace(']','')
    synthetic_data = synthetic_data.replace('\n','')
    synthetic_data = synthetic_data.replace(',','')
    synthetic_data = synthetic_data.split(' ')
    synthetic_data = np.array(synthetic_data, dtype=np.float64)
    print("\nSynthetic data received from server")
    print('Training Completed')
    return "1"


if __name__ == "__main__":
    app.run(port=5002,debug=True)
