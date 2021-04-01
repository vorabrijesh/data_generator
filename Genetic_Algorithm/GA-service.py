#from prediction_service import synthetic_data
from flask import Flask, request, session
import time, requests
import numpy as np
# from scipy.spatial import distance
# from sklearn.mixture import GaussianMixture
from heapq import nlargest
import random
# from Genetic_Rehearsal import *

from pymongo import MongoClient

'''
VERSION 3.0: Implementation of Genetic rehearsal algorithm in entirity.
Micro Services 
Pseudo Rehearsal 
Genetic Algorithm 
Workflow 
Multiple models 
session for each model 
controller, ga service, model service 
reliability level = 1 
pip installable
on the ga service side, mimic the model by a random forest regressor 
proxy model on the genetic algorithm side 
'''
app = Flask(__name__)
app.secret_key = "GA_SERVICE"
# Declare the global variables here
'''
flag_variable is used by client to see if images are ready for taking.
ready_flag is used by "server" to know whether predictions are ready on the client side to be collected.
training is used to stop the training process loop on the client side.
'''
# flag_variable = "0"
# ready_flag = "0"
# training_flag = "0"
# predictions = "nothing"
# synthetic_data = 0

ga = 0

def AddTuple(TUPLE, ELEMENT):
	TEMP = list(TUPLE)
	TEMP.insert(0, ELEMENT)
	return tuple(TEMP)

class GA:
	def __init__(self):
		self.flag_variable = "0"
		self.ready_flag = "0"
		self.training_flag = "0"
		self.predictions = "nothing"
		self.synthetic_data = 0
		self.images_variable = 0

	# Declare the main training function here
	def Start(self, test_data, num_generation):
		
		raw_data = test_data
		# cleaned_data = raw_data[2:len(raw_data)-1]
		split_data = raw_data.split(",")
		print(split_data)
		received_data = [int(x) for x in split_data]
		print("Final received labels: ", received_data)

		# Declaring the varibles required before hand. In the later versions, these will arrive as arguments.
		SHAPE = (28, 28)
		TARGET_CLASSES = received_data
		verbose = 1
		population_size = 8
		NUMBER_OF_CULTURES = 1
		NUMBER_OF_GENERATIONS = int(num_generation)
		MUTATION_PROBABILITY = 0.6
		MUTATION_TYPE = "+"
		best_list = []
		print("Set the training_flag to 1")
		self.training_flag = "1"

		# Declaring the variable
		temp_shape = AddTuple(SHAPE, 0)
		pseudo_x_train_2400 = np.zeros(temp_shape)

		POINTS_GATHERED = []
		ideal_points = []
		while (self.training_flag=="1"):
			
			for class_number in TARGET_CLASSES:
				POINTS_COUNTER = 0
				if verbose == 1:
					print(
					"\n\n\n ****************************************************************")
					print("Class number: ", class_number)
					print("****************************************************************")

				for p in range(NUMBER_OF_CULTURES):
					'''CREATING THE INITIAL POPULATION'''
					current_generation = []
					for i in range(population_size):
						current_generation.append(np.zeros(SHAPE))
					'''Declaring the stopping criteria for the genetic algorithm.'''
					best = 0
					

					#while best*100 < 99:
					for generation_number in range(NUMBER_OF_GENERATIONS):
						current_generation_fitness = []
						temp_shape = AddTuple(SHAPE, 1)
						for i in range(population_size):
							current_generation[i] = np.reshape(current_generation[i], temp_shape)
						self.images_variable = np.concatenate(current_generation, axis=0)
					
						# 3. SEND THE NUMPY ARRAY TO CLIENT
						self.flag_variable = "1"
						img = self.images(class_number)
						# 4. RECEIVE THE PREDICTIONS FROM CLIENT
						
						while self.ready_flag == "0":
							time.sleep(1)
						
						
						# print("Shape of received predictions is: ", predictions.shape)
						# print(type(predictions))
						self.predictions = np.reshape(self.predictions, (8, 1))
						# print("Reshaped predictions: ", predictions)

						# 5. UNWRAP THE PREDICTIONS AND APPEND TO current_generation_fitness list
						for i in range(population_size):
							class_prediction = np.argmax(self.predictions[i], axis=-1)
							fitness_score = self.predictions[i]

							current_generation_fitness.append(fitness_score)

						self.ready_flag = "0"
						self.flag_variable = "0"

						if max(current_generation_fitness) >= best:
							best = max(current_generation_fitness)
						if verbose == 1:
							print("Best: ", best*100, " Culture number: ", p, " Class number: ",class_number, "Generation no: ", generation_number)

						fittest_four_model_indices = nlargest(int(population_size/4), range(
						len(current_generation_fitness)), current_generation_fitness.__getitem__)
						temp_list = []
						for temp in range(int(population_size/4)):
							temp_list.append(np.copy(current_generation[fittest_four_model_indices[temp]]))

						for temp in range(int(population_size/4)):
							current_generation[temp] = np.copy(temp_list[temp])

						for temp in range((int(population_size/4)), (int(population_size/2))):
							current_generation[temp] = np.copy(current_generation[temp-(int(population_size/4))])

						for i in range((int(population_size/4)), (int(population_size/2))):
							# print('check point 1')
							point_mutation = np.random.choice([0, abs(np.random.normal(0, 1,[1]))],size=current_generation[i].shape, p=[(1-MUTATION_PROBABILITY),MUTATION_PROBABILITY])
							
							point_mutation = np.float64(point_mutation)
							
							if MUTATION_TYPE == "*":
								choice=random.choice(["+","-","*"])
								if choice== "-":
									current_generation[i] = current_generation[i] - point_mutation
								elif choice=="+":
									current_generation[i] = current_generation[i] + point_mutation
							elif MUTATION_TYPE == "+":
								current_generation[i] = current_generation[i] + point_mutation
							else:
								current_generation[i] = current_generation[i] - point_mutation
							#print('check point 2')
							
						for temp in range((int(population_size/2)), (int(population_size*0.75))):
							current_generation[temp] = np.copy(current_generation[temp-(int(population_size/2))])

						for temp in range((int(population_size/2)), (int(population_size*0.75))):
							if temp % 2 == 0:
								self.crossover(current_generation[temp], current_generation[temp+1], int((current_generation[temp].shape)[0]/2))

						for temp in range((int(population_size*0.75)), population_size):
							current_generation[temp] = np.copy(current_generation[temp-(int(population_size/2))])
						for temp in range((int(population_size*0.75)), population_size):
							if temp % 2 == 0:
								self.crossover(current_generation[temp], current_generation[temp+1], int((current_generation[temp].shape)[0]/2))
						
					for k in range(len(current_generation)):
						temp_shape = AddTuple(SHAPE, 1)
						pseudo_x_train_2400 = np.vstack((pseudo_x_train_2400, np.reshape(current_generation[k], temp_shape)))
			best_list.append(best*100)
			print("Generated data: ", pseudo_x_train_2400.shape)

			if verbose == 1:
				print("Training data shape: ", pseudo_x_train_2400.shape)

			# Load the global variable with synthetic data
			print(pseudo_x_train_2400.shape)
			synthetic_data = pseudo_x_train_2400.flatten()
			# synthetic_data =  str(list(synthetic_data))
			# synthetic_data = synthetic_data.replace('[','')
			# synthetic_data = synthetic_data.replace(']','')
			# synthetic_data = str(synthetic_data.tostring())
			synthetic_data = ','.join(str(x) for x in synthetic_data)
			print("Converted the synthetic data to string.")
			# set the training flag to 0
			self.training_flag = "0"
			print("Set the training flag to : ", self.training_flag)
		
		client = MongoClient('localhost', 27017)
		workflow =client['kali_db']['kali_wf']
		
		data = {}
		data['msg'] = {'type':'text','content':'synthetic_data'}
		# print(synthetic_data.shape)
		data['target_classes'] = {'type':'text','content':str(TARGET_CLASSES)}
		data['synthetic_data'] =  {'type':'text','content':synthetic_data}
		data['fitness_of_population'] = {'type':'text', 'content':str(best_list)}
		data['epochs']= {'type':'text', 'content':""}
		# data1 = json.dumps(data)
		workflow.insert_one(data)

		# data_service = client['kali_db']['data_service']
		# data_service.insert_one(data)
		# print('data stored into database...')
		# headers = { 'Content-Type': 'application/json'}
		# # try:
		# r = requests.post("http://127.0.0.1:5004/",data=data,headers=headers, timeout=1)
		# print(r.status_code)
		# # except:
		# # 	print('request completed')
		return 1

	# Declare the function that sends images to the client
	def images(self, class_number):
		client = MongoClient('localhost', 27017)
		workflow =client['kali_db']['kali_wf']
		data = {}
		data['msg'] = {'type':'text','content':'images'}
		data['target_class'] ={'type':'text','content': str(class_number)}
		print('images_variable.shape', self.images_variable.shape)
		flatten_images = self.images_variable.flatten()
		# print(images_variable[0])
		data['images'] ={'type':'text','content':str(list(flatten_images))}
		# print(data['images'])
		# data1 = json.dumps(data)
		workflow.insert_one(data)
		return self.images_variable

	def crossover(self,first_gene,second_gene,index):
		temp = np.copy(first_gene[index:])
		first_gene[index:] = second_gene[index:]
		second_gene[index:]=temp


	# declare the function that receives predictions from the client
	def fetch_predictions(self, pred):
		#global predictions
		# print("Predictions changed from", predictions)
		# predictions = request.data
		# print(pred)
		pred = pred.replace('[','')
		pred = pred.replace(']','')
		pred = pred.replace('\n','')
		pred = pred.split(' ')
		pred = [l for l in pred if l != ""]
		self.predictions = np.array(pred, dtype=np.float64)
		# predictions = pred
		# print("Predictions changed to", predictions)
		#global ready_flag
		self.ready_flag = "1"
		return "1"



# Declare the function that handles the Flag variable
@app.route('/GA', methods=['POST', 'GET'])
def ga_service():
	data = request.get_json()
	# print(data)
	if(data['msg']['content']== 'start_training'): # start_session
		test_data = data['test_data']['content']
		num_generation = data['number_of_generations']['content']
		print(num_generation)
		# session['id'] = data['id']['content']  # make new session, store msg in database and return controller that msg object.
		global ga
		ga = GA()
		ga.Start(test_data, num_generation)
		print('Started the training')
	if(data['msg']['content']=='predictions'):
		print('Fetching the predictions')
		ga.fetch_predictions(data['predictions']['content']) 
	# data['msg'] is to generate_data, then ga should generate data and put data in database. Data can be several data points.
	# data generated should be put into corresponding directory or should point to that id.
	# data['msg'] = predictions refer to corresponding session and then use them as fitness, by the corresponding ga instance.
	# ga should be a class
	# several instance of ga class should be there for each session. 
	# ga class should have 2 fun: 1) generate data points 2) receive fitness scores.
	return "1"



if __name__ == "__main__":
	app.run(port=5001,debug=True)
