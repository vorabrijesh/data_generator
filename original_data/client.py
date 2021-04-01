import requests
import time, json, random
import numpy as np

from flask import Flask, request, session, render_template

from pymongo import MongoClient
app = Flask(__name__)
app.secret_key = "client"

@app.route('/recieve_digits',methods=['GET','POST'])
def receive_digits():
    data = dict(request.form)
    msg = data['msg']
    data = data['data']
    data = data.replace('[','')
    data = data.replace(']','')
    data = data.replace('\n','')
    data = data.replace(',','')
    data = data.split(' ')
    data = np.array(data, dtype=np.float64)
    sh = int(data.shape[0]/64)
    data = np.reshape(data,(sh,64))
    print(data.shape)
    return "1"

@app.route('/recieve_boston',methods=['GET','POST'])
def receive_boston():
    data = dict(request.form)
    msg = data['msg']
    data = data['data']
    data = data.replace('[','')
    data = data.replace(']','')
    data = data.replace('\n','')
    data = data.replace(',','')
    data = data.split(' ')
    data = np.array(data, dtype=np.float64)
    data = np.reshape(data,(506,13))
    print(data.shape)
    return "1"
    
@app.route('/digits',methods=['GET','POST'])
def request_digits():
    if request.method =='GET':
        return render_template('digits.html')
    else:
        client = MongoClient('localhost',27017)
        workflow = client['data_generator']['od_wf']     
        # session['id'] = str(random.random())
        msg ={}
        data = request.form.to_dict()
        print(data)
        if 'entire' in data:
            msg['class'] = 'entire'
        else:
            cl = 0
            for i in range(10):
                if i in data:
                    cl = i
            msg['class'] = str(cl)
        print('requesting digits from service')
        msg['msg'] = 'recieve_digits'
        workflow.insert_one(msg)
        print('request completed')
        return "1"

@app.route('/boston',methods=['GET','POST'])
def request_boston():
    print('requesting boston data from service')
    client = MongoClient('localhost',27017)
    workflow = client['data_generator']['od_wf']     
    # session['id'] = str(random.random())
    msg ={}
    msg['msg'] = 'recieve_boston_data'
    workflow.insert_one(msg)
    print('request completed')
    return "1"


# @app.route('/client',methods=['GET','POST'])
# def client():
#     if request.method == 'GET':
#         request_data()
#     else:
#         data = dict(request.form)
#         digits = data['data']
#         receive_data(digits)
#     return "1"

if __name__ == "__main__":
    app.run(port=5001,debug=True)
