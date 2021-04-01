from datetime import datetime
from pymongo import MongoClient
import requests
import json

from requests.api import head


def conditionHandler(curr):
    client = MongoClient('localhost', 27017)
    wf_collection = client['kali_db']['kali_wf']
    node_collection = client['kali_db']['kali_node']
    # currNode = curr['nodeid']

    #currNode = curr['nodeid']['content']
    headers = { 'Content-Type': 'application/json'}
    
    data = curr
    id = curr['_id']
    data.pop('_id')
    data = json.dumps(data)
    msg = curr['msg']
    print(msg)
    if(curr['msg']['content'] == 'start_session'):
        try:
            r = requests.post("http://127.0.0.1:5002/model",data=data, headers=headers, timeout=1)
            # print(r.status_code)
            wf_collection.delete_one({'_id':id})
        except:
            print("Session Created... \n")
            pass
        curr['_id'] =id
        return ['controller'], curr
    elif(curr['msg']['content'] == 'start_training'):
        try:
            # requests.post("http://127.0.0.1:5000/",data=test_data, timeout=1)
            # print('check1')
            r = requests.post("http://127.0.0.1:5001/GA",data=data, headers=headers, timeout=1)
            # print(r.status_code)
            wf_collection.delete_one({'_id':id})
            # print('check2')
        except:
            wf_collection.delete_one({'_id':id})
            print("Training started... \n")
            pass
        return ['controller'], curr
    elif(curr['msg']['content'] == 'predictions'):
        
        try:
            # r = requests.post("http://127.0.0.1:5000/predictions",data=predictions) # /GA TODO 30dec 
            r = requests.post("http://127.0.0.1:5001/GA",data=data, headers=headers) 
            # print('prediction flag', r)
            wf_collection.delete_one({'_id':id})
        except:
            wf_collection.delete_one({'_id':id})
            print("Predictions Sent... \n")
        return ['controller'], curr

    elif(curr['msg']['content'] == 'images'):
        
        print('Deleting images from workflow...')
        # images = data['images']
        try:
            # requests.post("http://127.0.0.1:5001/p", data=images)  # TODO 30 Dec /model based on data it should change
            requests.post("http://127.0.0.1:5002/model", data=data, headers=headers)
            wf_collection.delete_one({'_id':id})
        except:
            wf_collection.delete_one({'_id':id})
            print("Images deleted...\n")
        return ['controller'], curr 
    elif(curr['msg']['content']=='synthetic_data'):
        curr['nodeid'] = {'type':'text','content':'controller'}
        return ['controller'], curr  
    elif(curr['msg']['content'] == 'retrain'):
                
        print('Sending data to data-service and training-service...')
        # synthetic_data = data['synthetic_data']
        client = MongoClient('localhost', 27017)
        data_service = client['kali_db']['data_service']
        # curr1 = curr
        # del curr1['_id']
        data_service.insert_one(curr)
        # print('Data stored to dataservice...')
        headers = { 'Content-Type': 'application/json'}
        try:
            r = requests.post("http://127.0.0.1:5004/",data=data,headers=headers, timeout=1)
            # print(r.status_code)
        except:
            print('Model Saved into database...')

        try:
            # requests.post("http://127.0.0.1:5001/synthetic_data", data=synthetic_data) # TODO 30Dec /model based on data it should change
            requests.post("http://127.0.0.1:5003/retrain", data=data , headers=headers)
            
            wf_collection.delete_one({'_id':id})
        except:
            wf_collection.delete_one({'_id':id})
            print("Retraining Completed... \n")
        return ['controller'], curr

    elif(curr['msg']['content'] == 'generate_gan_data'):
        try:
            r = requests.post("http://127.0.0.1:5005/gan",data=data, headers=headers) 
            # print('prediction flag', r)
            wf_collection.delete_one({'_id':id})
        except:
            wf_collection.delete_one({'_id':id})
            # print("Predictions Sent... \n")
        return ['controller'], curr

    elif(curr['msg']['content'] == 'gan_images'):
        
        print('Deleting gan images from workflow...')
        try:
            requests.post("http://127.0.0.1:5006/model", data=data, headers=headers)
            wf_collection.delete_one({'_id':id})
        except:
            wf_collection.delete_one({'_id':id})
            print("GAN Images deleted...\n")
        return ['controller'], curr
    
    elif(curr['msg']['content'] == 'gan_predictions'):
        curr['nodeid'] = {'type':'text','content':'controller'}
        return ['controller'], curr  
    
    ## gmm
    elif(curr['msg']['content'] == 'generate_gmm_data'):
        try:
            r = requests.post("http://127.0.0.1:5007/gmm",data=data, headers=headers) 
            # print('prediction flag', r)
            wf_collection.delete_one({'_id':id})
        except:
            wf_collection.delete_one({'_id':id})
            # print("Predictions Sent... \n")
        return ['controller'], curr

    elif(curr['msg']['content'] == 'gmm_images'):
        
        print('Deleting gan images from workflow...')
        try:
            requests.post("http://127.0.0.1:5008/model", data=data, headers=headers)
            wf_collection.delete_one({'_id':id})
        except:
            wf_collection.delete_one({'_id':id})
            print("GAN Images deleted...\n")
        return ['controller'], curr
    
    
    elif(curr['msg']['content'] == 'gmm_predictions'):
        curr['nodeid'] = {'type':'text','content':'controller'}
        return ['controller'], curr  
        

    return None, curr
# conditionHandler()
