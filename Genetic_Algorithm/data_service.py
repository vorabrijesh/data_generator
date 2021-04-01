import requests
import time, json, random
import numpy as np
from flask import Flask, request, session

from pymongo import MongoClient
app = Flask(__name__)
app.secret_key = "data_service"



@app.route('/', methods= ['GET','POST'])
def store_data():
    data = request.get_json()
    print('data received...')
    print('storing data into database...')
    client = MongoClient('localhost', 27017)
    data_service = client['kali_db']['data_service']
    data_service.insert_one(data)
    print('data stored into database...')
    return "1"



if __name__ == "__main__":
    app.run(port=5004,debug=True)
