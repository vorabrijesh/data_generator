from flask import Flask, request, session
from sklearn import datasets
import numpy as np
import random
from pymongo import MongoClient
import tensorflow as tf
from keras.datasets import mnist
from keras.models import load_model
from numpy import expand_dims
from numpy import zeros
from numpy import ones
from numpy import vstack
from numpy.random import randn
from numpy.random import randint
app = Flask(__name__)
app.secret_key = "gan_service"

# generate points in latent space as input for the generator
def generate_latent_points(latent_dim, n_samples):
	# generate points in the latent space
	x_input = randn(latent_dim * n_samples)
	# reshape into a batch of inputs for the network
	x_input = x_input.reshape(n_samples, latent_dim)
	return x_input

# use the generator to generate n fake examples, with class labels
def generate_fake_samples(g_model, latent_dim, n_samples):
	# generate points in latent space
	x_input = generate_latent_points(latent_dim, n_samples)
	# predict outputs
	X = g_model.predict(x_input)
	# create 'fake' class labels (0)
	y = zeros((n_samples, 1))
	return X, y

def send_digits(data):

	new_model = tf.keras.models.load_model('generator_model_020.h5')
	print(new_model.summary())
	
	model = load_model('generator_model_020.h5')
	latent_dim =100
	X, y = generate_fake_samples(model, latent_dim, 60)
	print(X.shape)
	print(y.shape)

	flatten_data = X.flatten()
	print(flatten_data.shape)
	try:
		client = MongoClient('localhost', 27017)
		workflow =client['kali_db']['kali_wf']
		
		# data = {}
		data['msg'] = {'type':'text','content':'gan_images'}
		data['images'] =  {'type':'text','content':str(list(flatten_data))}
		
		workflow.insert_one(data)
	except:
		print('error sending data')
	return "1"


@app.route('/gan', methods=['GET','POST'])
def gan():
	data = request.get_json()
    # print(data)
	if(data['msg']['content']=='generate_gan_data'):
		send_digits(data)
	return "1"
if __name__ == "__main__":
	app.run(port='5005',debug=True)
