# data ={
#     "jobid": {
#         "type": "text",
#         "content": 1
#     },
#     "job_name": {
#         "type": "text",
#         "content": "ga"
#     },
#     "role": {
#         "type": "text",
#         "content": "ga"
#     },
#     "nodeid": {
#         "type": "text",
#         "content": "controller"
#     },
#     "nstatus": {
#         "type": "text",
#         "content": "pending"
#     },
#     "msg": {
#         "type": "text",
#         "content": "start_training"
#     },
#     "id": {
#         "type": "text",
#         "content": "408"
#     },
#     "test_data": {
#         "type": "text",
#         "content": "0,1"
#     }
# }
# import requests, json
# data = json.dumps(data)
from pymongo import MongoClient
# headers = { 'Content-Type': 'application/json'}
# try:
#     r = requests.post("http://127.0.0.1:5001/GA",data=data, headers=headers, timeout=2)
#     print(r.status_code)
#     client = MongoClient('localhost', 27017)
#     wf_collection = client['kali_db']['kali_wf']
#     # wf_collection.delete_one({'msg':})

# except:
    # print('request completed')
import numpy as np
client = MongoClient('localhost', 27017)
node_collection = client['kali_db']['kali_node']

row = node_collection.find_one({'msg':{'type':'text','content':'retrain'}})

data = row['synthetic_data']['content']
data = data.replace("b",'')
data = data.replace("'","")
data = data.encode('utf-8')
print(type(data))
# print(data)
print(np.frombuffer(data, dtype=np.float32))