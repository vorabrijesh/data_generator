
from pymongo import MongoClient
client = MongoClient('192.168.1.111',27017)
workflow =client['kali_db']['kali_wf']

# print(data)
workflow.insert_one({"hi":"hello"})