from flask import Flask, request, session
from sklearn import datasets
import numpy as np
import random
import pickle
from pymongo import MongoClient

# from keras.datasets import mnist

app = Flask(__name__)
app.secret_key = "gmm_service"

# @app.route('/digits',methods=['GET','POST'])
def send_digits(msg):
	# print('sending digits from service to client') 
	filename='finalized_model.sav'

	loaded_model = pickle.load(open(filename, 'rb'))

	synthetic_data = loaded_model.sample(n_samples=50)
	flatten_digits = synthetic_data[0].flatten()
	print(flatten_digits.shape)
	try:
		client = MongoClient('localhost', 27017)
		workflow =client['kali_db']['kali_wf']
		msg['msg'] = {'type':'text','content':'gmm_images'}
		msg['images'] =  {'type':'text','content':str(list(flatten_digits))}
		workflow.insert_one(msg)
	except:
		print('error sending data')
	return "1"


@app.route('/gmm', methods=['GET','POST'])
def gmm():
	data = request.get_json()
    # print(data)
	if(data['msg']['content']=='generate_gmm_data'):
		send_digits(data)
	return "1"
if __name__ == "__main__":
	app.run(port='5007',debug=True)
