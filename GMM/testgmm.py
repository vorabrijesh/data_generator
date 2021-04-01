import pickle
import numpy as np
from sklearn.mixture import GaussianMixture
import tensorflow as tf
# from keras.datasets import mnist

filename='finalized_model.sav'
# pickle.dump(gm, open(filename, 'wb'))
loaded_model = pickle.load(open(filename, 'rb'))

synthetic_data = loaded_model.sample(n_samples=50)

images = synthetic_data[0]

loaded_model = tf.keras.models.load_model("ML_MODEL")

predictions = loaded_model.predict_classes(images)
    
print(predictions)
# labels = np.reshape(labels,(int(labels.shape[0]/784),28,28))
target_class = [0]
extracted_data = images[np.where(predictions==target_class)]
print(extracted_data)