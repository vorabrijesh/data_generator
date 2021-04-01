from flask import Flask, request, session
from sklearn import datasets
import numpy as np
import random
from pymongo import MongoClient


app = Flask(__name__)
app.secret_key = "original_data"

@app.route('/digits',methods=['GET','POST'])
def send_digits():
	print('sending digits from service to client') 
	digits = datasets.load_digits()
	X = digits.data
	y = digits.target

	client_msg = request.form.to_dict()
	data_class = client_msg['class']

	if data_class != 'entire':
		data_class = int(data_class)
		X = X[y == data_class]
		
	print(X.shape)
	flatten_digits = X.flatten()
	print(flatten_digits.shape)
	try:
		msg ={}
		msg['msg'] = 'send_digits'
		msg['data'] = str(list(flatten_digits))
	
		client = MongoClient('localhost', 27017)
		workflow = client['data_generator']['od_wf']
		workflow.insert_one(msg)
	except:
		print('error sending data')
	return "1"

@app.route('/boston_data',methods=['GET','POST'])
def send_boston():
	print('sending boston data from service to client') 
	# session['id'] = str(int(random.random()*1000))
	data = datasets.load_boston()
	digits = data['data']
	labels = data['target']
	
	print(digits.shape)
	flatten_digits = digits.flatten()
	print(flatten_digits.shape)
	try:
		msg ={}
		msg['msg'] = 'send_boston_data'
		msg['data'] = str(list(flatten_digits))
	
		client = MongoClient('localhost', 27017)
		workflow = client['data_generator']['od_wf']
		workflow.insert_one(msg)
	except:
		print('error sending data')
	return "1"
if __name__ == "__main__":
	app.run(debug=True)
