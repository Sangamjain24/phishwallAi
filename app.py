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

# Global Safelist of trusted domains to ensure 100% accuracy for common sites
TRUSTED_DOMAINS = {
    'google.com', 'google.co.in', 'facebook.com', 'instagram.com', 'whatsapp.com', 
    'chatgpt.com', 'openai.com', 'youtube.com', 'github.com', 'linkedin.com', 
    'twitter.com', 'x.com', 'amazon.com', 'amazon.in', 'netflix.com', 
    'wikipedia.org', 'microsoft.com', 'apple.com', 'vercel.app', 'vercel.com',
    'gmail.com', 'yahoo.com', 'outlook.com', 'bing.com', 'duckduckgo.com',
    'reddit.com', 'stackoverflow.com', 'medium.com', 'spotify.com', 'canva.com',
    'zoom.us', 'pinterest.com', 'quora.com', 'dropbox.com', 'adobe.com',
    'wixsite.com', 'weebly.com', 'blogspot.com', 'netlify.app', 'web.app',
    'firebaseapp.com', 'pages.dev', '000webhostapp.com', 'godaddy.com'
}

def is_on_safelist(url):
    try:
        from urllib.parse import urlparse
        domain = urlparse(url).netloc.lower()
        if domain.startswith('www.'):
            domain = domain[4:]
        
        # Check if the domain itself is in our list
        if domain in TRUSTED_DOMAINS:
            return True
        
        # Check if it's a subdomain of a trusted domain
        for trusted in TRUSTED_DOMAINS:
            if domain.endswith('.' + trusted):
                return True
        return False
    except:
        return False

# Brand Protection: Keywords often misused in subdomains
SUSPICIOUS_KEYWORDS = {
    'att', 'paypal', 'microsoft', 'apple', 'google', 'login', 'secure', 
    'account', 'verify', 'billing', 'support', 'amazon', 'bank', 'netflix',
    'security', 'update', 'signin', 'service', 'office', 'wallet', 'crypto'
}

def is_highly_suspicious(url):
    try:
        from urllib.parse import urlparse
        domain_parts = urlparse(url).netloc.lower().split('.')
        # If there's a subdomain (e.g., att1.godaddysites.com)
        if len(domain_parts) > 2:
            subdomain = domain_parts[0]
            base_domain = domain_parts[1]
            
            for keyword in SUSPICIOUS_KEYWORDS:
                # If keyword is in subdomain but NOT in the base domain
                # e.g., 'att1' in 'godaddysites.com' but NOT 'att.com'
                if keyword in subdomain and keyword not in base_domain:
                    return True
        return False
    except:
        return False

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
        
        # 1. Check Safelist first
        if is_on_safelist(url):
            name = [url, "Safe", "Continue", "1"]
            return render_template("index.html", name=name)
        
        # 2. Check for Brand Hijacking (Highly Suspicious)
        if is_highly_suspicious(url):
            name = [url, "Not Safe", "Suspicious Brand Keyword Detected", ""]
            return render_template("index.html", name=name)

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

    # 1. Check Safelist first
    if is_on_safelist(url):
        return jsonify({
            'url': url,
            'prediction': 'Safe',
            'action': 'Continue',
            'is_safe': True
        })
    
    # 2. Check for Brand Hijacking (Highly Suspicious)
    if is_highly_suspicious(url):
        return jsonify({
            'url': url,
            'prediction': 'Not Safe',
            'action': 'Suspicious Brand Keyword Detected',
            'is_safe': False
        })

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
