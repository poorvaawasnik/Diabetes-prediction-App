import numpy as np

def preprocess_input(data):
    return np.array(data).reshape(1, -1)
