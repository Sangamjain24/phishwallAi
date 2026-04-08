import numpy as np
import pickle
from feature import FeatureExtraction
from convert import convertion

# Load the model
with open("newmodel.pkl", "rb") as file:
    gbc = pickle.load(file)

url = "http://match.lookatmynewphotos.com/"

# Extract features
obj = FeatureExtraction(url)
x = np.array(obj.getFeaturesList()).reshape(1, 30)

# Predict
y_pred = gbc.predict(x)[0]
result = convertion(url, int(y_pred))

print(f"URL: {url}")
print(f"Prediction: {result[1]}")
print(f"Action: {result[2]}")
print(f"Features: {obj.getFeaturesList()}")
