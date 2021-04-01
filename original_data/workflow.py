from pymongo import MongoClient
from time import sleep
import requests
import numpy as np
#engine infinite loop
client = MongoClient('localhost',27017)
workflow = client['data_generator']['od_wf']  

while True :

     
    print('Workflow Running')
    sleep(3)

    #just process one pending job at a time
    for data in workflow.find():
        
        
        try:
            # print(type(data))
            msg = data['msg']
            if(msg == 'send_digits'):
                print('WF processing...')
                query = workflow.delete_one({'_id':data['_id']})
                del data['_id']        
                print(query)
                try:
                    requests.post("http://127.0.0.1:5001/recieve_digits",data=data, timeout=1)
                except:
                    print("Request completed \n")
                
            if(msg == 'send_boston_data'):
                print('WF processing...')
                query = workflow.delete_one({'_id':data['_id']})
                del data['_id']        
                print(query)
                try:
                    requests.post("http://127.0.0.1:5001/recieve_boston",data=data, timeout=1)
                except:
                    print("Request completed \n")

            if (msg == 'recieve_digits'):
                print('WF processing...')
                query = workflow.delete_one({'_id':data['_id']})
                del data['_id']        
                print(query)
                try:
                    requests.post("http://127.0.0.1:5000/digits",data=data)
                except:
                    print("Request completed \n")
                
            if (msg == 'recieve_boston_data'):
                print('WF processing...')
                query = workflow.delete_one({'_id':data['_id']})
                del data['_id']        
                print(query)
                try:
                    requests.post("http://127.0.0.1:5000/boston_data",data=data)
                except:
                    print("Request completed \n")
           
        except:
            print('error processing the workflow')
            pass
    
        break
    # end for loop
# end while loop
