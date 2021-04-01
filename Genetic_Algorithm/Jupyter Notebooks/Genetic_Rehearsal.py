from scipy.spatial import distance
import numpy as np
import keras
from sklearn.mixture import GaussianMixture
from heapq import nlargest
import random


def crossover(first_gene,second_gene,index):
  temp = np.copy(first_gene[index:])
  first_gene[index:] = second_gene[index:]
  second_gene[index:]=temp

def duplicate_remover(dataset,fitness_list):
  duplicate_count=0
  duplicate_index = [i for i in range(len(dataset))]

  for i in range(len(dataset)):
    if duplicate_index[i] != "D":
      j=i
      while j+1 < len(dataset):
        # if distance.euclidean(np.reshape(dataset[i],(784,)),np.reshape(dataset[j+1],(784,))) == 0:
        if distance.euclidean(np.reshape(dataset[i],(2,)),np.reshape(dataset[j+1],(2,))) == 0:
          duplicate_count += 1
          # print("Duplicate found @: ",j+1)
          fitness_list[j+1] = 0
          duplicate_index[j+1] = "D"
        j += 1

  return duplicate_count

def duplicate_counter(dataset):
  duplicate_count=0
  for i in range(len(dataset)):
    j=i
    while j+1 < len(dataset):
      if distance.euclidean(np.reshape(dataset[i],(784,)),np.reshape(dataset[j+1],(784,))) == 0:
        duplicate_count += 1
      j += 1

  return duplicate_count

def generate_labels(data,model,number_of_classes):
  '''
  . \n\n
  AUTHOR:
  Suri Bhasker Sri Harsha

  AIM:
  The function assigns labels to the given dataset with the given model as the reference.
  The function returns a list with labels in two formats. The first format is the one-hot encoding
  format and the second format is the binary format of labels.

  ARGUMENTS:
  data: The dataset for which you want to generate labels
  model: The model that will be used for the label generation
  number_of_classes: Number of classes in the dataset

  RETURNS:
  [labels, pre_labels]
  '''

  labels = model.predict_classes(data,verbose=1)
  pre_labels = labels
  labels = keras.utils.to_categorical(labels,number_of_classes)

  return [labels,pre_labels]

def confidence_filter(data, model, number_of_samples, verbose=0):

  '''
  . \n\n
  AUTHOR:
  Suri Bhasker Sri Harsha

  AIM:
  The function was developed to "filter" out points that are closer
  to the decision boudary compared to others. The function has the following arguments

  ARGUMENTS:
  data: The dataset in which you want to select the points closest to the decision boundary
  model: The model that will be used as the fitness function
  number_of_samples: Number of boundary points you want to achieve
  verbose: Default is 0. Displays the progress of the function
  '''
  predictions = model.predict(data,verbose=verbose)
  standard_deviations = np.std(predictions,axis=1)
  indices = np.argsort(standard_deviations)[:number_of_samples]

  print(indices.shape)
  return indices

def agreement_score(model1_predictions, model2_predictions):

  '''
  Returns the degree of agreement between predictions of two models

  INPUT ARGUMENTS
  model1_predictions: Preditions of the model 1 on a test dataset
  model2_predictions: Preditions of the model 2 on a test dataset

  OUTPUT:
  Returns a list of two elements where the first elements is the
  "Agreement score" between the two lists and the second element
  is the list of indices where both the models have agreed upon.
  '''

  if len(model1_predictions) != len(model2_predictions):
    print("Length of given lists donot match")
    return 0

  correct_count = 0
  agreement_indices = []

  for i in range(len(model1_predictions)):
    if model1_predictions[i] == model2_predictions[i]:
      correct_count += 1
      agreement_indices.append(i)

  agreement_score = (correct_count/len(model1_predictions))*100

  return [agreement_score, agreement_indices]


def Enrichment(data,labels,model,NUMBER_OF_CENTERS,NUMBER_OF_CLASSES, NUMBER_OF_SAMPLES, verbose=0):
    '''
    Enriches the given data by fitting a Gaussian Mixture model with
    NUMBER_OF_CENTERS and NUMBER_OF_SAMPLES
    '''
    if verbose == 1:
        print("Creating the Gaussian mixture model ...")
    gaussian = GaussianMixture(n_components = NUMBER_OF_CENTERS)

    if verbose == 1:
        print("Created the model ...")

    if verbose == 1:
        print("Fitting the data to the GMM ...")
    gaussian.fit(X=data)

    if verbose == 1:
        print("Generating synthetic samples ....")
    synthetic = gaussian.sample(n_samples=NUMBER_OF_SAMPLES)

    synthetic_data = synthetic[0]

    if verbose == 1:
        print("Generating labels ...")
    labels = model.predict_classes(synthetic_data,verbose=1)
    pre_labels = labels
    labels = keras.utils.to_categorical(labels,NUMBER_OF_CLASSES)

    return [synthetic_data, labels, pre_labels]
def interleaved_rehearsal(model, NEW_DATA, REHEARSAL_DATA, OLD_TEST_DATA, NEW_TEST_DATA,epochs=20):

  '''

  Performs interleaved rehearsal of NEW_DATA and REHEARSAL_DATA on Model and returns the model

  OUTPUT FORMAT:
  DATA :== [data, labels]


  '''
  # Unpacking all the data
  new_data = NEW_DATA[0]
  new_labels = NEW_DATA[1]

  rehearsal_data = REHEARSAL_DATA[0]
  rehearsal_labels = REHEARSAL_DATA[1]

  old_test_data = OLD_TEST_DATA[0]
  old_test_labels = OLD_TEST_DATA[1]

  new_test_data = NEW_TEST_DATA[0]
  new_test_labels = NEW_TEST_DATA[1]

  accuracy_with_genetic_rehearsal=[]
  learning_with_genetic_rehearsal=[]

  for i in range(epochs):

    model.fit(new_data,new_labels,batch_size=100,epochs=1,verbose=1)
    model.fit(rehearsal_data,rehearsal_labels,batch_size=1000,epochs=1,verbose=1)

    score = model.evaluate(old_test_data,old_test_labels)

    accuracy_with_genetic_rehearsal.append(score[1])

    learning_score = model.evaluate(new_test_data,new_test_labels)
    print("Epoch Number: %d, Retention: %f, Learning: %f " %(i,score[1],learning_score[1]))
    learning_with_genetic_rehearsal.append(learning_score[1])

  return [accuracy_with_genetic_rehearsal, learning_with_genetic_rehearsal]

def AddTuple(TUPLE, ELEMENT):
    TEMP = list(TUPLE)
    TEMP.insert(0, ELEMENT)

    return tuple(TEMP)

'''The following things are to be added to the code::
Version 2.0:: Create the Generate Genetic data function.
Version 3.0:: Create the GRehearse() function.
Version 4.0:: Test the code for CNNs.
Version 5.0:: Add functions to reduce number of points generated in Enrichment phase
'''

def Genetic_data_Generator(model,SHAPE,TARGET_CLASSES,verbose=1,population_size=16,NUMBER_OF_CULTURES = 30,NUMBER_OF_GENERATIONS = 100,MUTATION_PROBABILITY = 0.1,MUTATION_TYPE = "+"):
    '''
    The function takes in the model and target classes and generates synthetic data using Genetic Algorithm.
    OUTPUT FORMAT: [synthetic_data, synthetic_labels]

    VARIABLE DESCRIPTION::

    model: Input the Keras built neural network.
    SHAPE: Input the shape of sample in dataset. Example for MNIST digits, input ::SHAPE=(28,28,1)
    TARGET_CLASSES: List of all the target classes for which synthetic data is generated.
    verbose: Displays the intermediate output of algorithm if set to 1. Default is 1.
    population_size: Size of population in each culture. Minimum of 4.
    NUMBER_OF_CULTURES: Number of cultures in Genetic algorithm.
    NUMBER_OF_GENERATIONS: Default set to 100. Ignore if selecting other stopping criteria.
    MUTATION_PROBABILITY: A value between 0 and 1 which decides the probability of a pixel getting mutated.
    MUTATION_TYPE: Default = "+"; Options = "+","-","*";"+" signifies a positive mutation, "-" signifies a negative mutation and "*" signifies a random mutation.

    '''

    # To do::
    # CHECK POINT 3::
    # CHECK POINT 5: Selection mechanism can be added as a parameter
    # Generalize the number of classes variable in the code
    '''
    pseudo_x_train_2400 is the numpy array in which the synthetic dataset that is generated finally sits.
    '''
    temp_shape = AddTuple(SHAPE,0)
    pseudo_x_train_2400 = np.zeros(temp_shape)
    # pseudo_x_train_2400 = np.zeros((0,784))

    '''
    Variables for debugging purposes. Not mandatory
    # POINTS_GATHERED = [] UNCOMMENT IF REQUIRED
    # ideal_points = [] UNCOMMENT IF REQUIRED
    '''
    POINTS_GATHERED = []
    ideal_points = []

    for class_number in TARGET_CLASSES:
        '''This loop is responsible for iterating through classes.'''
        POINTS_COUNTER=0
        if verbose == 1:
            print("Class number: ", class_number)

        ''' POINTS_COUNTER is a redundant variable and can be used for debugging purposes.
            It was declared to keep the number of point generated per each class.
            It has no significane if the code is being run with fixed number of cultures for fixed number of generations.
        # POINTS_COUNTER=0 UNCOMMENT IF REQUIRED`
        '''

        '''This loop creates multiple cultures to ensure genetic diversity in the final population.'''
        for p in range(NUMBER_OF_CULTURES):

            '''CREATING THE INITIAL POPULATION'''
            current_generation=[]
            for i in range(population_size):

                # CHECK POINT 1:
                current_generation.append(np.zeros(SHAPE))

            '''Declaring the stopping criteria for the genetic algorithm.'''
            # CHECK POINT 2:
            best = 0
            best_list = []

            while best*100 < 99:
            # for generation_number in range(NUMBER_OF_GENERATIONS):

                '''Finding fitness of each sample in the generation.'''
                current_generation_fitness=[]
                for i in range(population_size):

                    # CHECK POINT 3:: Write code to generalize the shape
                    temp_shape = AddTuple(SHAPE,1)
                    test_point = np.reshape(current_generation[i],temp_shape)

                    # CHECK POINT 4: Can include Verbose parameter.
                    fitness_score = model.predict(test_point)[0][class_number]
					# fitness_score = model(test_point) PyTorch syntax
                    class_prediction= model.predict_classes(test_point)
                    # print("Fitness: ",fitness_score," Prediction: ",class_prediction, "organism: ",i)
                    # print(current_generation_fitness)
                    current_generation_fitness.append(fitness_score)


                if max(current_generation_fitness) >= best:
                    best = max(current_generation_fitness)

                if verbose == 1:
                    print("Best: ",best*100, " Culture number: ",p," Class number: ",class_number)

                # CHECK POINT 5:: Selection mechanisms can be added as a parameter.
                # print("Number of duplicates: ",duplicate_remover(current_generation,current_generation_fitness))
                fittest_four_model_indices = nlargest(int(population_size/4), range(len(current_generation_fitness)), current_generation_fitness.__getitem__)
                # fittest_four_model_indices = roulette_selection(current_generation_fitness,verbose=0)

                # VERIFIED
                temp_list=[]
                for temp in range(int(population_size/4)):
                    temp_list.append(np.copy(current_generation[fittest_four_model_indices[temp]]))


                # VERIFIED
                for temp in range(int(population_size/4)):
                    current_generation[temp] = np.copy(temp_list[temp])


                ''' Mutations'''
                for temp in range((int(population_size/4)),(int(population_size/2))):
                    current_generation[temp] = np.copy(current_generation[temp-(int(population_size/4))])


                # VERIFIED
                for i in range((int(population_size/4)),(int(population_size/2))):
                    # point_mutation=np.random.choice([-0.5,1],size=current_generation[i].shape, p=[0.99,0.01])
                    # point_mutation=np.random.choice([0,np.random.normal(0,1,[1])],size=current_generation[i].shape, p=[0.99,0.01])
                    point_mutation=np.random.choice([0,abs(np.random.normal(0,1,[1]))],size=current_generation[i].shape, p=[(1-MUTATION_PROBABILITY),MUTATION_PROBABILITY])
                    # point_mutation=np.random.choice([0,1],size=current_generation[i].shape, p=[0.9,0.1])

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


                '''Crossover'''
                for temp in range((int(population_size/2)),(int(population_size*0.75))):
                    current_generation[temp] = np.copy(current_generation[temp-(int(population_size/2))])


                # VERIFIED
                for temp in range((int(population_size/2)),(int(population_size*0.75))):
                    if temp%2 == 0:
                        crossover(current_generation[temp],current_generation[temp+1],int((current_generation[temp].shape)[0]/2))
                        # crossover(current_generation[10],current_generation[11],int((current_generation[10].shape)[0]/2))

                '''mutated crossover'''
                for temp in range((int(population_size*0.75)),population_size):
                    current_generation[temp] = np.copy(current_generation[temp-(int(population_size/2))])

                for temp in range((int(population_size*0.75)),population_size):
                    if temp%2 == 0:
                        crossover(current_generation[temp],current_generation[temp+1],int((current_generation[temp].shape)[0]/2))

            ''' Adding a culture after reaching the stopping criteria to the final dataset'''
            for k in range(len(current_generation)):
                temp_shape = AddTuple(SHAPE,1)
                pseudo_x_train_2400 = np.vstack((pseudo_x_train_2400,np.reshape(current_generation[k],temp_shape)))


        print("Generated data: ",pseudo_x_train_2400.shape)


        '''Creating labels for the generated synthetic dataset'''

        pseudo_y_train_2400 = model.predict_classes(pseudo_x_train_2400)
        pre_pseudo_y_train_2400 = pseudo_y_train_2400
        pseudo_y_train_2400 = keras.utils.to_categorical(pseudo_y_train_2400, 20)
        if verbose == 1:
            print("Training data shape: ",pseudo_x_train_2400.shape)
            print("Training labels shape: ",pseudo_y_train_2400.shape)


    return [pseudo_x_train_2400, pseudo_y_train_2400]
