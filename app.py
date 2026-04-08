#importing required libraries

from flask import Flask, request, render_template, jsonify
from flask_cors import CORS
import numpy as np
import pandas as pd
from sklearn import metrics
import warnings
import pickle
from convert import convertion
warnings.filterwarnings('ignore')
from feature import FeatureExtraction

file = open("newmodel.pkl","rb")
gbc = pickle.load(file)
file.close()


app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return render_template("index.html")

@app.route('/result',methods=['POST','GET'])
def predict():
    if request.method == "POST":
        url = request.form["name"]
        obj = FeatureExtraction(url)
        x = np.array(obj.getFeaturesList()).reshape(1,30)
    
        y_pred =gbc.predict(x)[0]
        name=convertion(url,int(y_pred))
        return render_template("index.html", name=name)
    return render_template("index.html")

@app.route('/usecases', methods=['GET', 'POST'])
def usecases():
    return render_template('usecases.html')

@app.route('/api/predict', methods=['POST'])
def api_predict():
    data = request.get_json()
    url = data['url']
    obj = FeatureExtraction(url)
    x = np.array(obj.getFeaturesList()).reshape(1,30)
    y_pred = gbc.predict(x)[0]
    
    # Debug logging for Vercel
    print(f"DEBUG: URL={url}, Prediction={y_pred}")
    print(f"DEBUG: Features={obj.getFeaturesList()}")
    
    # Use convertion logic for consistency with web UI
    result = convertion(url, int(y_pred))
    label = result[1] # "Safe" or "Not Safe"
    is_safe = (int(y_pred) == 1 and result[1] == "Safe")
    
    return jsonify({
        'url': url,
        'prediction': label,
        'action': result[2],
        'is_safe': is_safe
    })

if __name__ == "__main__":
    app.run(debug=True)
