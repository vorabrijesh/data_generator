from posix import listdir
from pymongo import MongoClient
client = MongoClient('localhost', 27017)
model = client['kali_db']['models']
import pathlib
import os
import numpy as np
import base64
def save_model():
    data ={}
    data['name'] = "ML_MODEL"
    mypath = '/home/brijesh/Desktop/data_generator/Genetic-Pseudo-Rehearsal-master/API/ML_MODEL'

    
    for path in pathlib.Path(mypath).iterdir():
        if path.is_file():
            current_file = open(path, "r+b")
            data['saved_model'] = current_file.read()
            # print(current_file.read())
            current_file.close()
        else:
            dir = listdir(path)
            for f in dir:
                mypath1 = str(path)+'/'+f
                current_file = open(mypath1,"r+b")
                f = f.split('.')
                data[f[1]] = current_file.read()
                current_file.close()

    model.insert_one(data)


def retrieve_model():
    row =  model.find_one({'name':'ML_MODEL_TEST'})
    mypath = '/home/brijesh/Desktop/data_generator/Genetic-Pseudo-Rehearsal-master/API/'+row['name']
    try:
        os.mkdir(mypath)
    except:
        print('directory already present')
    try:
        os.mkdir(mypath+'/variables')
    except:
        print('directory already present')
    
    # print(row)
    del row['_id']
    with open(mypath+"/saved_model.pb", "wb") as f:
        f.write(row['saved_model'])
    del row['saved_model']
    del row['name']
    for key, value in row.items():
        with open(mypath+'/variables/variables.'+key, "wb") as f:
            f.write(value)

        # print(key)

retrieve_model()
